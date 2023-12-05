import distutils.util
import os

ENV_NAME = os.environ.get("ENV_NAME", "local")

NODE_URL = os.environ.get("NODE_URL", "https://bsc-dataseed1.binance.org/")
GITHUB_URL = os.environ.get("GITHUB_URL",
                            "https://raw.githubusercontent.com/pancakeswap/pancake-frontend/develop/packages/ifos/src/constants/ifos/bsc.ts")

TARGET_NAME = os.environ.get("TARGET_NAME", "nginx")
TARGET_NAMESPACE = os.environ.get("TARGET_NAMESPACE", "default")
TARGET_API_VERSION = os.environ.get("TARGET_API_VERSION", "apps.kruise.io/v1alpha1")
TARGET_KIND = os.environ.get("TARGET_KIND", "CloneSet")
SCALEDOBJECT_NAME = os.environ.get("SCALEDOBJECT_NAME", "bsc-so")

K8S_REPLICAS_COUNT = int(os.environ.get("K8S_REPLICAS_COUNT", "5"))

HOURS_BEFORE_SCALE = int(os.environ.get("HOURS_BEFORE_SCALE", "2"))
HOURS_AFTER_SCALE = int(os.environ.get("HOURS_AFTER_SCALE", "2"))

AVAILABLE_CLEARANCE_MINUTES = int(os.environ.get("AVAILABLE_CLEARANCE_MINUTES", "20"))

MAX_REPLICA_COUNT = int(os.environ.get("MAX_REPLICA_COUNT", "30"))
MIN_REPLICA_COUNT = int(os.environ.get("MIN_REPLICA_COUNT", "2"))
POLLING_INTERVAL = int(os.environ.get("POLLING_INTERVAL", "60"))
IDLE_REPLICA_COUNT = int(os.environ.get("IDLE_REPLICA_COUNT", "0"))

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = os.environ.get("TELEGRAM_CHAT_IDS", "").split(',')

TIMEZONE = os.environ.get("TIMEZONE", "UTC")

LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'INFO').upper()

DRY_RUN = bool(distutils.util.strtobool(os.environ.get('DRY_RUN', 'True')))
