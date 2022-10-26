import logging
from keda import Keda
from telegram import Telegram
from pancakeswap import PancakeIFO
from settings import LOGGING_LEVEL, NODE_URL

logger = logging.getLogger('info-scaler')

if __name__ == '__main__':
    logging.basicConfig(level=LOGGING_LEVEL)

    k = Keda()
    t = Telegram()
    ifo = PancakeIFO(node_url=NODE_URL)

    iofs = ifo.get_active_ifos()
    new_ifos = k.patch_scaledobject(iofs)

    for i in new_ifos:
        t.broadcast_messages(f"Prepared to IFO {i['name']}: "
                             f"Scaling start time: {i['start'].strftime('%c')}")
