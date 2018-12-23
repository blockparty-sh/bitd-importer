#!/usr/bin/env python3

import os 
import json
import base64
import argparse
import binascii
import pymongo
from dotenv import load_dotenv
from blockchain_parser.block import Block
import bitcoin.rpc
import tna

load_dotenv()

btc_conf_file = os.path.expanduser(os.getenv("BTC_CONF_FILE"))

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]
#db.confirmed.delete_many({}) # clear old data (done in parallel)

parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--start-block", type=int, required=True, help="block to start")
parser.add_argument("--end-block", type=int, required=True, help="block to start")
parser.add_argument("--dry", action="store_true", help="dry run (no inserts)")
parser.add_argument("--verbose", action="store_true", help="show json from tna")
args = parser.parse_args()

rpc = bitcoin.rpc.RawProxy(btc_conf_file=btc_conf_file)

for height in range(args.start_block, args.end_block):
    block_hash = rpc.getblockhash(height)
    raw_block  = binascii.unhexlify(rpc.getblock(block_hash, False)) # set to 0 to get raw hex data

    block = Block(raw_block, height=height)

    documents = []
    for tx in block.transactions:
        res = tna.extract(block, tx)
        if args.verbose:
            print(json.dumps(res, indent=4))
        documents.append(res)

    if args.dry:
        inserted = 0
    else:
        inserted = len(db.confirmed.insert_many(documents).inserted_ids)

    print("{}%\theight={} inserted={}".format(
        round((block.height-args.start_block) / (args.end_block-args.start_block) * 100, 2),
        block.height,
        inserted
    ))

