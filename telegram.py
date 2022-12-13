import logging
import requests
from urllib.parse import urlencode

import settings
from settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_IDS, ENV_NAME


class TelegramClientInitError(Exception):
    def __str__(self):
        return 'Telegram client not configured'


class Telegram:
    def __init__(self):
        self.logger = logging.getLogger('telegram')

        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_IDS:
            raise TelegramClientInitError()

    def __make_request(self, method, **kwargs):
        qstr = urlencode(kwargs)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}?{qstr}"
        return requests.get(url).json()

    def send_message(self, chat_id, text):
        text = "{}: {}".format(ENV_NAME, text)
        if settings.DRY_RUN:
            print('DRY_RUN mode: {}'.format(text))
        else:
            return self.__make_request('sendMessage', chat_id=chat_id, text=text)

    def broadcast_messages(self, text):
        for chat_id in TELEGRAM_CHAT_IDS:
            self.send_message(chat_id, text)
