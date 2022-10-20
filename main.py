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
    active_scaledobjects = []
    for i in active_ifos:
        start_datetime, end_datetime = ifo.get_ifo_period(i['address'])

        logger.info(f"Found IFO {i['name']} from {start_datetime} to {end_datetime}")

        if end_datetime <= now:
            logger.info(f"IFO {i['name']} expired")
            continue

        scaledobject_name, preparing_start_datetime = k.create_scaledobjects(i['address'], i['name'], start_datetime,
                                                                             end_datetime)
        active_scaledobjects.append(scaledobject_name)

        if preparing_start_datetime:
            t.broadcast_messages(f"Prepared to IFO {i['name']}, address {i['address']}. "
                                 f"Scaling start time: {preparing_start_datetime.strftime('%c')}")

    # cleanup scaleobjects
    deleted_scaleobjects = k.delete_scaledobjects(active_scaledobjects)
    for s in deleted_scaleobjects:
        t.broadcast_messages(f"Deprecated scaledObject {s} deleted")
