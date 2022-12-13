import yaml
import logging
import datetime
from kubernetes import client, config
from jinja2 import Environment, FileSystemLoader, select_autoescape

from settings import K8S_REPLICAS_COUNT, HOURS_BEFORE_SCALE, TARGET_NAME, TARGET_NAMESPACE, TIMEZONE, \
    TARGET_API_VERSION, TARGET_KIND, SCALEDOBJECT_NAME, DRY_RUN


class Keda:
    KEDA_API = "keda.sh"
    KEDA_VERSION = "v1alpha1"

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

    def patch_scaledobject(self, ifos):
        ifo_triggers = []
        new_triggers = []
        new_addresses = set()

        current_resource = self.customObjectApi.get_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION,
                                                                             TARGET_NAMESPACE,
                                                                             'scaledobjects', SCALEDOBJECT_NAME)
        currents_addresses = set(current_resource['metadata']['annotations'].
                                 get('ifo-scaler.predictkube.com/contract-addresses', '').split(','))

        for i in ifos.copy():
            i['start_cron'] = self.__datetime_to_cron(i['start'] - datetime.timedelta(hours=HOURS_BEFORE_SCALE))
            i['end_cron'] = self.__datetime_to_cron(i['end'])
            ifo_triggers.append(i)
            new_addresses.add(i['address'])
            if i['address'] not in currents_addresses:
                new_triggers.append(i)


        scaledobject_yml = self.__render_scaledobject(scaledobject_name=SCALEDOBJECT_NAME, namespace=TARGET_NAMESPACE,
                                                      target_name=TARGET_NAME,
                                                      target_api_version=TARGET_API_VERSION, target_kind=TARGET_KIND,
                                                      timezone=TIMEZONE,
                                                      replicas=K8S_REPLICAS_COUNT,
                                                      ifo_triggers=ifo_triggers,
                                                      addresses=",".join(new_addresses))

        if DRY_RUN:
            self.logger.info('DRY_RUN mode: scaledobject_yml conftent below:')
            print(scaledobject_yml)
        else:
            self.customObjectApi.patch_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION,
                                                                TARGET_NAMESPACE,
                                                                'scaledobjects', SCALEDOBJECT_NAME,
                                                                yaml.load(scaledobject_yml, Loader=yaml.FullLoader))

        return new_triggers
