import json
import yaml
import base64
import hashlib
import logging
import datetime
import dateutil.parser
from kubernetes import client, config
from jinja2 import Environment, FileSystemLoader, select_autoescape
from kubernetes.client import ApiException

from settings import K8S_REPLICAS_COUNT, HOURS_BEFORE_SCALE, TARGET_NAME, TARGET_NAMESPACE, TIMEZONE, \
    TARGET_API_VERSION, TARGET_KIND, SCALEDOBJECT_NAME, DRY_RUN, MAX_REPLICA_COUNT, MIN_REPLICA_COUNT, POLLING_INTERVAL, \
    IDLE_REPLICA_COUNT, HOURS_AFTER_SCALE, AVAILABLE_CLEARANCE_MINUTES


def datetime_parser(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = dateutil.parser.parse(value)
        except (ValueError, AttributeError, TypeError):
            pass
    return json_dict


class Keda:
    KEDA_API = "keda.sh"
    KEDA_VERSION = "v1alpha1"
    TRIGGERS_CONF_PATH = "./conf/triggers.yaml"

    def __init__(self):
        self.logger = logging.getLogger('keda')

        try:
            self.config = config.load_incluster_config()
        except:
            self.config = config.load_kube_config()

        self.k8s_client = client.ApiClient(configuration=self.config)
        self.customObjectApi = client.CustomObjectsApi(self.k8s_client)

        self.jinja = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape()
        )

    def __datetime_to_cron(self, dt):
        return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"

    def __render_scaledobject(self, **kwargs):
        template = self.jinja.get_template("scaledobject.yaml.jinja2")
        return template.render(**kwargs)

    def __get_settings_checksum(self):
        m = hashlib.sha256()

        for i in [TARGET_NAME, TARGET_NAMESPACE, TARGET_API_VERSION, TARGET_KIND, SCALEDOBJECT_NAME, K8S_REPLICAS_COUNT,
                  HOURS_BEFORE_SCALE, HOURS_AFTER_SCALE, AVAILABLE_CLEARANCE_MINUTES, MAX_REPLICA_COUNT,
                  MIN_REPLICA_COUNT, POLLING_INTERVAL, IDLE_REPLICA_COUNT, TIMEZONE]:
            m.update(str(i).encode('utf8'))

        return m.hexdigest()

    def get_triggers(self):
        with open(self.TRIGGERS_CONF_PATH, 'r') as f:
            data = yaml.safe_load(f)
        return data

    def __is_update_required(self, current_resource, settings_checksum: str, ifos: list) -> bool:
        try:
            previous_ifos_data = current_resource['metadata']['annotations'].get('ifo-scaler.predictkube.com/ifos', '')
            old_settings_checksum = current_resource['metadata']['annotations'].get(
                'ifo-scaler.predictkube.com/checksum', '')

            decoded_ifos_data = base64.b64decode(previous_ifos_data).decode('utf8')
            previous_ifos = json.loads(decoded_ifos_data, object_hook=datetime_parser)
            previous_data = dict([(i['address'], i) for i in previous_ifos])

            if old_settings_checksum != settings_checksum:
                self.logger.info('Settings was changed. Need to update scaledobject.')
                return True

            for ifo in ifos:
                if (ifo['start'] - previous_data[ifo['address']]['start']) > datetime.timedelta(
                        minutes=AVAILABLE_CLEARANCE_MINUTES):
                    self.logger.info('Start date changed for IFO {}'.format(ifo['name']))
                    return True
                if (ifo['end'] - previous_data[ifo['address']]['end']) > datetime.timedelta(
                        minutes=AVAILABLE_CLEARANCE_MINUTES):
                    self.logger.info('End date changed for IFO {}'.format(ifo['name']))
                    return True
        except:
            self.logger.warning('Scaledobject {}.{} have can not checked. Path required.'.format(SCALEDOBJECT_NAME,
                                                                                                 TARGET_NAMESPACE))
            return True

        return False

    def patch_scaledobject(self, ifos: list) -> list:
        ifo_triggers = []
        current_resource = None
        triggers = self.get_triggers()

        try:
            current_resource = self.customObjectApi.get_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION,
                                                                                 TARGET_NAMESPACE,
                                                                                 'scaledobjects', SCALEDOBJECT_NAME)
        except ApiException:
            self.logger.warning('Scaledobject {}.{} not found'.format(SCALEDOBJECT_NAME, TARGET_NAMESPACE))

        settings_checksum = self.__get_settings_checksum()

        if current_resource and not self.__is_update_required(current_resource, settings_checksum, ifos):
            self.logger.info('No changes needed. Exit.')
            return []

        for i in ifos.copy():
            i['start_scaling'] = i['start'] - datetime.timedelta(hours=HOURS_BEFORE_SCALE)
            i['end_scaling'] = i['end'] + datetime.timedelta(hours=HOURS_AFTER_SCALE)
            i['start_cron'] = self.__datetime_to_cron(i['start_scaling'])
            i['end_cron'] = self.__datetime_to_cron(i['end_scaling'])
            ifo_triggers.append(i)

        ifos_info = base64.b64encode(json.dumps(ifos, default=str).encode('utf8')).decode('utf8')
        scaledobject_yml = self.__render_scaledobject(scaledobject_name=SCALEDOBJECT_NAME, namespace=TARGET_NAMESPACE,
                                                      target_name=TARGET_NAME,
                                                      target_api_version=TARGET_API_VERSION, target_kind=TARGET_KIND,
                                                      timezone=TIMEZONE,
                                                      replicas=K8S_REPLICAS_COUNT,
                                                      triggers=yaml.safe_dump(triggers),
                                                      ifo_triggers=ifo_triggers,
                                                      ifos_info=ifos_info,
                                                      settings_checksum=settings_checksum,
                                                      maxReplicaCount=MAX_REPLICA_COUNT,
                                                      minReplicaCount=MIN_REPLICA_COUNT,
                                                      pollingInterval=POLLING_INTERVAL,
                                                      idleReplicaCount=IDLE_REPLICA_COUNT)

        if DRY_RUN:
            self.logger.info('DRY_RUN mode: scaledobject_yml content below:')
            self.logger.info(scaledobject_yml)
        else:
            if current_resource:
                self.customObjectApi.patch_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION,
                                                                    TARGET_NAMESPACE, 'scaledobjects',
                                                                    SCALEDOBJECT_NAME,
                                                                    yaml.load(scaledobject_yml,
                                                                              Loader=yaml.FullLoader))
            else:
                self.customObjectApi.create_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION,
                                                                     TARGET_NAMESPACE, 'scaledobjects',
                                                                     yaml.load(scaledobject_yml,
                                                                               Loader=yaml.FullLoader))
            self.logger.info('Scaledobject {}.{} updated'.format(SCALEDOBJECT_NAME, TARGET_NAMESPACE))

        return ifo_triggers
