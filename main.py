import logging
from keda import Keda
from telegram import Telegram
from pancakeswap import PancakeIFO
from settings import LOGGING_LEVEL, NODE_URL, TIMEZONE

logger = logging.getLogger('info-scaler')

if __name__ == '__main__':
    logging.basicConfig(level=LOGGING_LEVEL)

    k = Keda()
    t = Telegram()
    ifo = PancakeIFO(node_url=NODE_URL)

    iofs = ifo.get_active_ifos()
    new_ifos = k.patch_scaledobject(iofs)

    for i in new_ifos:
        t.broadcast_messages(f"Prepared to IFO {i['name']}:\n"
                             f"Start IFO: {i['start'].strftime('%c')}\n"
                             f"End IFO: {i['end'].strftime('%c')}\n"
                             f"Scaling from: {i['start_scaling'].strftime('%c')} to {i['end_scaling'].strftime('%c')}\n"
                             f"Timezone: {TIMEZONE}")
