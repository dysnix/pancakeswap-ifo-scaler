# pancakeswap-ifo-scaler

Auto-scaler for Pancakeswap Blockchain Nodes Infrastructure.

## Principle algorithm

1. Event of new [Pancakeswap IFO](https://pancakeswap.finance/ifo)
2. Create k8s resource [KEDA scaleobject](https://keda.sh/docs/2.7/scalers/cron/)
3. Resize blockchain cluster by scaling pod
4. Send notification to Telegram (by [@predictkube_bot](https://t.me/predictkube_bot))
