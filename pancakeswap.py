import datetime
import json
import logging
import re
import json5
import requests
from web3 import Web3
from settings import HOURS_BEFORE_SCALE, GITHUB_URL


class PancakeIFO:
    def __init__(self, node_url="https://bsc-dataseed1.binance.org/",
                 github_info_url=GITHUB_URL):
        self.logger = logging.getLogger('pancakeswap')

        self.node_url = node_url
        self.github_info_url = github_info_url

        self.web3 = Web3(Web3.HTTPProvider(node_url))
        with open('./abi/ifoV2.json') as f:
            self.abi = json.load(f)

    def get_github_page(self):
        return requests.get(self.github_info_url).text

    def parse_ifo_page(self, data):
        js_obj = '[{}]'.format(re.search(r'Ifo\[\] = \[((?:\n.+)+)\n]', data, re.MULTILINE).group(1))
        js_obj = re.sub(r'bscTokens\.\w+', '""', js_obj)
        js_obj = re.sub(r'cakeBnbLpToken', '""', js_obj)
        js_obj = re.sub(r'`', '"', js_obj)
        return json5.loads(js_obj)

    def get_active_ifos(self):
        js_code = self.get_github_page()
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        result = []
        active_ifos = [ifo for ifo in self.parse_ifo_page(js_code) if ifo['isActive']]
        for i in active_ifos:
            start_datetime, end_datetime = self.get_ifo_period(i['address'])

            self.logger.info(f"Found IFO {i['name']} from {start_datetime} to {end_datetime}")

            if end_datetime <= now:
                self.logger.info(f"IFO {i['name']} expired")
                continue

            result.append({
                'name': i['name'],
                'address': i['address'],
                'start': start_datetime,
                'end': end_datetime
            })
        return result

    def get_ifo_period(self, contact_address):
        contract = self.web3.eth.contract(address=contact_address, abi=self.abi)

        start_block = contract.functions.startBlock().call()
        end_block = contract.functions.endBlock().call()

        start_block_diff = start_block - self.web3.eth.blockNumber
        end_block_diff = end_block - self.web3.eth.blockNumber

        start_datetime = datetime.datetime.now() + datetime.timedelta(seconds=start_block_diff * 3)
        end_datetime = datetime.datetime.now() + datetime.timedelta(seconds=end_block_diff * 3)

        return start_datetime.astimezone(datetime.timezone.utc), end_datetime.astimezone(datetime.timezone.utc)
