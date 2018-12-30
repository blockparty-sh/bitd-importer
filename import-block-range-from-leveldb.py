#!/usr/bin/env python3

import os 
import argparse
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from blockchain_parser.blockchain import Blockchain
import tna
import util


load_dotenv()

blocks_path = os.path.expanduser(os.getenv("BLOCKS_PATH"))
index_path  = os.path.expanduser(os.getenv("INDEX_PATH"))
cache_path  = os.path.expanduser(os.getenv("CACHE_PATH"))

conn = psycopg2.connect(user=os.getenv("POSTGRES_USER"),
                        password=os.getenv("POSTGRES_PASSWORD"),
                        database=os.getenv("POSTGRES_DB"))
cur = conn.cursor()


parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--start-block", type=int, required=True, help="block to start")
parser.add_argument("--end-block", type=int, help="block to finish on, if not given will get last one in index cache")
parser.add_argument("--bulk-amount", type=int, default=10000, help="how many documents to process before doing insert")
parser.add_argument("--dry", action="store_true", help="dry run (no inserts)")
parser.add_argument("--verbose", action="store_true", help="show json from tna")
args = parser.parse_args()

blockchain = Blockchain(blocks_path)
util.build_index_cache(index_path, cache_path, blockchain)

if not args.end_block:
    args.end_block = util.count_leveldb_last_block(index_path, cache_path, start_block, blockchain)

documents = []
for block in blockchain.get_ordered_blocks(
    index=index_path,
    cache=cache_path,
    start=args.start_block,
    end=args.end_block
):
    print("{}%\theight={}\ttxs={}".format(
        round((block.height-args.start_block) / (args.end_block-args.start_block) * 100, 2),
        block.height,
        len(block.transactions)
    ))

    for tx in block.transactions:
        res = tna.extract(block, tx)
        if args.verbose:
            print(json.dumps(res, indent=4))
        documents.append(res)

        if not args.dry and len(documents) >= args.bulk_amount:
            util.insert_documents(cur, documents)
            documents = []


# insert remaining documents
if not args.dry:
    util.insert_documents(cur, documents)
    documents = []

conn.commit()
cur.close()
conn.close()
