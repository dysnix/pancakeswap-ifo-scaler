import logging

import yaml
from datetime import timedelta
from kubernetes import client, config
from kubernetes.client import ApiException

from settings import K8S_REPLICAS_COUNT, HOURS_BEFORE_SCALE, TARGET_NAME, TARGET_NAMESPACE, TIMEZONE, \
    TARGET_API_VERSION, TARGET_KIND


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

    def __datetime_to_cron(self, dt):
        return f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"

    def create_scaledobjects(self, contract_address, name, start_datetime, ifo_end_datetime,
                             replicas=K8S_REPLICAS_COUNT,
                             hours_before_scale=HOURS_BEFORE_SCALE,
                             namespace=TARGET_NAMESPACE, target_name=TARGET_NAME,
                             timezone=TIMEZONE):

        preparing_start_datetime = start_datetime - timedelta(hours=hours_before_scale)

        scaledobject_name = 'ifo-{}-{}'.format(contract_address, name).lower()

        with open('./keda/scaledobject.yaml', 'r') as tpl:
            scaledobject_yml = tpl.read().format(contract_address=contract_address, name=scaledobject_name,
                                                 namespace=namespace, target_name=target_name,
                                                 target_api_version=TARGET_API_VERSION, target_kind=TARGET_KIND,
                                                 timezone=timezone,
                                                 start=self.__datetime_to_cron(preparing_start_datetime),
                                                 end=self.__datetime_to_cron(ifo_end_datetime), replicas=replicas)

        try:
            self.customObjectApi.create_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION, namespace,
                                                                 'scaledobjects',
                                                                 yaml.load(scaledobject_yml, Loader=yaml.FullLoader))
        except ApiException as e:
            if e.status == 409:
                self.logger.warning('ScaledObject {} already exist'.format(name))
                return scaledobject_name, None
            else:
                self.logger.error('ScaledObject {} already can not be created: {}'.format(name, str(e)))
                return scaledobject_name, None

        return scaledobject_name, preparing_start_datetime

    def delete_scaledobjects(self, scaledobjects, namespace=TARGET_NAMESPACE):
        deleted_scaledobjects = []
        scalers = self.customObjectApi.list_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION, namespace,
                                                                     'scaledobjects',
                                                                     label_selector='app.kubernetes.io/managed-by=predictkube')

        items = dict(scalers)['items']
        exist_scalers = [s['metadata']['name'] for s in items]

        for scaledobject in exist_scalers:
            if scaledobject not in scaledobjects:
                self.logger.info('scaleobject {} was deprecated. Deleting...'.format(scaledobject))
                self.customObjectApi.delete_namespaced_custom_object(self.KEDA_API, self.KEDA_VERSION, namespace,
                                                                     'scaledobjects', scaledobject)
                self.logger.warning('Scaleobject {} deleted'.format(scaledobject))
                deleted_scaledobjects.append(scaledobject)

        return deleted_scaledobjects
