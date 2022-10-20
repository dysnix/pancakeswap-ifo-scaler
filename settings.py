import os

ENV_NAME = os.environ.get("ENV_NAME", "local")

NODE_URL = os.environ.get("NODE_URL", "https://bsc-dataseed1.binance.org/")

TARGET_NAME = os.environ.get("TARGET_NAME", "nginx")
TARGET_NAMESPACE = os.environ.get("TARGET_NAMESPACE", "default")
TARGET_API_VERSION = os.environ.get("TARGET_API_VERSION", "apps.kruise.io/v1alpha1")
TARGET_KIND = os.environ.get("TARGET_NAMETARGET_KINDSPACE", "CloneSet")

K8S_REPLICAS_COUNT = int(os.environ.get("K8S_REPLICAS_COUNT", "5"))

HOURS_BEFORE_SCALE = int(os.environ.get("HOURS_BEFORE_SCALE", "2"))

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

TIMEZONE = os.environ.get("TIMEZONE", "UTC")
CHATS_FILE_PATH = os.environ.get("CHATS_FILE_PATH", "./data/chats.json")

LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO').upper()
