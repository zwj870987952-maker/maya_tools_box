import json
from pathlib import Path


class PackageData:
    @staticmethod
    def get_data():
        return json.loads((Path(__file__).with_name('bundle')/'eblabs_hub/WorldSpaceTools/data/eblabs.data').read_text(encoding='utf-8-sig'))


class Version:
    @staticmethod
    def print_version_info():
        print('WorldSpaceTools supplied native source:',PackageData.get_data().get('version'))
