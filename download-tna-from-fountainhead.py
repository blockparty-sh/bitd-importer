import base64
import argparse
import json
import requests

parser = argparse.ArgumentParser(description="grab tna/tx from fountainhead")
parser.add_argument("--txid", type=str, required=True, help="txid to grab")
args = parser.parse_args()


url = "https://bitdb.fountainhead.cash/q/{}".format(
    base64.b64encode(json.dumps({
        "v": 3,
        "q": {
            "find": {"tx.h": args.txid},
            "limit": 1
         }
    }).encode()).decode('utf-8')
)

r = requests.get(url)
res = r.content
parsed = json.loads(res.decode('utf-8'))

print(json.dumps(parsed["c"][0], sort_keys=True, indent=4))
