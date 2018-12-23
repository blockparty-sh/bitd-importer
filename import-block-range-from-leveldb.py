#!/usr/bin/env python3

import os 
import argparse
import pymongo
import json
from dotenv import load_dotenv
from blockchain_parser.blockchain import Blockchain
import tna


load_dotenv()

blocks_path = os.path.expanduser(os.getenv("BLOCKS_PATH"))
index_path  = os.path.expanduser(os.getenv("INDEX_PATH"))
cache_path  = os.path.expanduser(os.getenv("CACHE_PATH"))

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]
#db.confirmed.delete_many({}) # clear old data (done in parallel)

blockchain = Blockchain(blocks_path)

try:
    open(cache_path, 'r')
    print('found existing cache')
except FileNotFoundError:
    print('building cache, this may take a long time')


parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--start-block", type=int, required=True, help="block to start")
parser.add_argument("--end-block", type=int, required=True, help="block to start")
parser.add_argument("--dry", action="store_true", help="dry run (no inserts)")
parser.add_argument("--verbose", action="store_true", help="show json from tna")
args = parser.parse_args()

for block in blockchain.get_ordered_blocks(
    index=index_path,
    cache=cache_path,
    start=args.start_block,
    end=args.end_block
):
    #print("height=%d block=%s" % (block.height, block.hash))
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
