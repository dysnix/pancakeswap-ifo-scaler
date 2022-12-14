# pancakeswap-ifo-scaler

Auto-scaler for Pancakeswap Blockchain Nodes Infrastructure.

## Principle algorithm

1. Event of new [Pancakeswap IFO](https://pancakeswap.finance/ifo)
2. Create k8s resource [KEDA scaleobject](https://keda.sh/docs/2.7/scalers/cron/)
3. Resize blockchain cluster by scaling pod
4. Send notification to Telegram (by [@predictkube_bot](https://t.me/predictkube_bot))
5. Cleanup k8s resources

## Config environment variables


* `TARGET_NAME` - Kubernetes target controller for scaling (**required**)
* `TARGET_NAMESPACE` - Kubernetes namespace with controller (**required**)
* `K8S_REPLICAS_COUNT` - Replicas count for IFO period (**required**)
* `TELEGRAM_TOKEN` - Token for notification (**required**)
* `TARGET_API_VERSION` - Kubernetes target controller API version (default is `apps.kruise.io/v1alpha1`)
* `TARGET_KIND` - Kubernetes target controller Kind (default is `CloneSet`)
* `NODE_URL` - BSC JsonRPC Endpoint. Public endpoint by default

## Run

Please add [@predictkube_bot](https://t.me/predictkube_bot) to any telegram group(s) for receive notifications.

### Locally

    export TELEGRAM_TOKEN="changeme"
    pip install -r requirements.txt
    python main.py

### Docker

    docker build -t ifo-scaler .
    docker run -v $HOME/.kube:/root/.kube -e TELEGRAM_TOKEN="changeme" ifo-scaler
