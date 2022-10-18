import os

NODE_URL = os.environ.get("NODE_URL", "https://bsc-dataseed1.binance.org/")

K8S_CONTROLLER_NAME = os.environ.get("K8S_CONTROLLER_NAME", "nginx")
K8S_CONTROLLER_NAMESPACE = os.environ.get("K8S_CONTROLLER_NAMESPACE", "default")
K8S_REPLICAS_COUNT = int(os.environ.get("K8S_REPLICAS_COUNT", "5"))

HOURS_BEFORE_SCALE = int(os.environ.get("HOURS_BEFORE_SCALE", "2"))

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

TIMEZONE = os.environ.get("TIMEZONE", "UTC")
CHATS_FILE_PATH = os.environ.get("CHATS_FILE_PATH", "./data/chats.json")

LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO').upper()