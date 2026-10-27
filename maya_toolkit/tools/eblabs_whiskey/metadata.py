import json
from pathlib import Path


class PackageData:
    @staticmethod
    def get_data():
        return json.loads((Path(__file__).parent / 'upstream/eblabs_hub/Whiskey/data/eblabs.data').read_text(encoding='utf-8-sig'))
