import json
import logging
import os.path
import requests
from urllib.parse import urlencode
from settings import TELEGRAM_TOKEN, CHATS_FILE_PATH, ENV_NAME


class TelegramClientInitError(Exception):
    def __str__(self):
        return 'TELEGRAM_TOKEN env variable not provided'


class Telegram:
    def __init__(self):
        self.logger = logging.getLogger('telegram')

        if not TELEGRAM_TOKEN:
            raise TelegramClientInitError()

        self.chat_mkids = self.__load_chat_ids()

    def __make_request(self, method, **kwargs):
        qstr = urlencode(kwargs)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}?{qstr}"
        return requests.get(url).json()

    def __load_chat_ids(self):
        chat_ids = self.__get_chats()

        if os.path.isfile(CHATS_FILE_PATH):
            with open(CHATS_FILE_PATH, 'r') as f:
                res = json.load(f)
                exist_chat_ids = list(res['chat_ids'])
                chat_ids.update(exist_chat_ids)

        self.chat_ids = chat_ids

        # force save chats
        os.makedirs(os.path.dirname(CHATS_FILE_PATH), exist_ok=True)
        with open(CHATS_FILE_PATH, 'w') as f:
            json.dump({"chat_ids": list(self.chat_ids)}, f)

    def __get_chats(self):
        chat_ids = set()
        data = self.__make_request('getUpdates')

        for res in data['result']:
            membership = res.get('my_chat_member')
            if membership:
                chat_ids.add(membership['chat']['id'])

        return chat_ids

    def send_message(self, chat_id, text):
        text = "{}: {}".format(ENV_NAME, text)
        return self.__make_request('sendMessage', chat_id=chat_id, text=text)

    def broadcast_messages(self, text):
        for chat_id in self.chat_ids:
            self.send_message(chat_id, text)
