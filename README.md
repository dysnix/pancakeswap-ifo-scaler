# pancakeswap-ifo-scaler

Auto-scaler for Pancakeswap Blockchain Nodes Infrastructure.

## Principle algorithm

1. Event of new [Pancakeswap IFO](https://pancakeswap.finance/ifo)
2. Create k8s resource [KEDA scaleobject](https://keda.sh/docs/2.7/scalers/cron/)
3. Resize blockchain cluster by scaling pod
4. Send notification to Telegram (by [@predictkube_bot](https://t.me/predictkube_bot))

## Config environment variables

* `K8S_CONTROLLER_NAME` - Kubernetes target controller for scaling
* `K8S_CONTROLLER_NAMESPACE` - Kubernetes namespace with controller
* `K8S_REPLICAS_COUNT` - Replicas count for IFO period
* `TELEGRAM_TOKEN` - **required** token for notification
* `NODE_URL` - BSC JsonRPC Endpoint. Public endpoint by default

## Run

### Locally

    pip install -r requirements.txt
    python main.py

### Docker

    docker build -t ifo-scaler .