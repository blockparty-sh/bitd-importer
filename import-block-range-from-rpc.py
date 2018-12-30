#!/usr/bin/env python3

import os 
import sys
import json
import base64
import argparse
import binascii
import pymongo
from dotenv import load_dotenv
from blockchain_parser.block import Block
import bitcoin.rpc
import tna
import util

load_dotenv()

btc_conf_file = os.path.expanduser(os.getenv("BTC_CONF_FILE"))

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]

parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--start-block", type=int, help="block to start, if not given will go from db.meta.last_block")
parser.add_argument("--end-block", type=int, help="block to finish on, if not given will go until rpc fails")
parser.add_argument("--bulk-amount", type=int, default=10000, help="how many documents to process before doing insert")
parser.add_argument("--dry", action="store_true", help="dry run (no inserts)")
parser.add_argument("--verbose", action="store_true", help="show json from tna")
args = parser.parse_args()

rpc = bitcoin.rpc.RawProxy(btc_conf_file=btc_conf_file)

last_block_height = util.meta_get_last_block_height(db)
if not args.start_block:
    if last_block_height is not None:
        args.start_block = last_block_height + 1
    else:
        args.start_block = 0

if last_block_height is not None:
    if args.start_block < last_block_height:
        print("start_block is smaller than last block height in db ({})".format(last_block_height))
        print("this means you are rescanning parts of the blockchain you've already scanned")
        print("the entries will be deleted, and this is safe, it just might take longer")
        if input("press enter to continue, anything else to exit: ") != "":
            sys.exit()
    if args.start_block-1 > last_block_height:
        print("start_block-1 is greater than last block height in db ({})".format(last_block_height))
        print("this might mean you are skipping blocks")
        if input("press enter to continue, anything else to exit: ") != "":
            sys.exit()

# this is just used for printing status
percentage_end_block_count = args.end_block

# if end_block not provided we should keep going until an error occurs
if not args.end_block:
    args.end_block = 999999999
    percentage_end_block_count = rpc.getblockcount()


total_blocks = args.end_block - args.start_block

if not args.dry:
    print('deleted {} txs from gte block {}'.format(
        util.delete_txs_gte(db, args.start_block),
        args.start_block
    ))

for height in range(args.start_block, args.end_block):
    try:
        block_hash = rpc.getblockhash(height)
    except bitcoin.rpc.JSONRPCError as e:
        print('cannot get block hash, breaking')
        break

    raw_block  = binascii.unhexlify(rpc.getblock(block_hash, False)) # set to 0 to get raw hex data

    block = Block(raw_block, height=height)

    print("{}%\theight={} txs={}".format(
        round((block.height-args.start_block) / (percentage_end_block_count-args.start_block) * 100, 2),
        block.height,
        len(block.transactions)
    ))

    documents = []
    for tx in block.transactions:
        res = tna.extract(block, tx)
        if args.verbose:
            print(json.dumps(res, indent=4))
        documents.append(res)

        if not args.dry and len(documents) >= args.bulk_amount:
            inserted = len(db.confirmed.insert_many(documents).inserted_ids)
            util.meta_update_last_block_height(db, height)

