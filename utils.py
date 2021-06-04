import json
import base64


def to_base64(obj: object) -> bytes:
    return base64.b64encode(json.dumps(obj).encode())


def from_base64(raw_bytes) -> object:
    return json.loads(base64.b64decode(raw_bytes))


class Jsoner:
    @staticmethod
    def get(filename):
        with open(filename) as f:
            return json.load(f)

    def dump(self, obj, filename):
        with open(filename, 'w') as f:
            return json.dump(obj, f, ensure_ascii=False, indent=4)
