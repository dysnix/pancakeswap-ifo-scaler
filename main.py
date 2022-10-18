import logging
import datetime
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

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    active_ifos = ifo.get_active_ifos()

    # create scaleobjects
    scaledobjects = []
    for i in active_ifos:
        start_datetime, end_datetime = ifo.get_ifo_period(i['address'])

        logger.info(f"Found IFO {i['name']} from {start_datetime} to {end_datetime}")

        if end_datetime <= now:
            logger.info(f"IFO {i['name']} expired.")
            continue

        scaledobject_name, preparing_start_datetime = k.create_scaledobjects(i['address'], i['name'], start_datetime,
                                                                             end_datetime)
        scaledobjects.append(scaledobject_name)

        if preparing_start_datetime:
            t.broadcast_messages(f"Prepared to IFO {i['name']}, address {i['address']}. "
                                 f"Scaling start time: {preparing_start_datetime.strftime('%c')}")

    # cleanup scaleobjects
    map(lambda s: t.broadcast_messages(f"Deprecated scaledobject {s} deleted"),
        k.delete_scaledobjects(scaledobjects))
