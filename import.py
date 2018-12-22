#!/usr/bin/env python3

import os
import pymongo
import subprocess
import argparse
from blockchain_parser.blockchain import Blockchain
from dotenv import load_dotenv

load_dotenv()

blocks_path = os.path.expanduser(os.getenv("BLOCKS_PATH"))
index_path  = os.path.expanduser(os.getenv("INDEX_PATH"))
cache_path  = os.path.expanduser(os.getenv("CACHE_PATH"))

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]
db.confirmed.delete_many({}) # clear old data

parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--start-block", type=int, required=True, help="block to start")
parser.add_argument("--end-block", type=int, required=True, help="block to start")
parser.add_argument("--par", type=int, required=True, help="amount of processes to divide load between")
args = parser.parse_args()


blockchain = Blockchain(blocks_path)

try:
    open(cache_path, 'r')
    print('found existing cache')
except FileNotFoundError:
    print('building cache, this may take a long time')
    for block in blockchain.get_ordered_blocks(
        index=index_path,
        cache=cache_path,
    ):
        break

total_blocks = args.end_block - args.start_block

brange = []
for i in range(args.par):
    brange.append((
        (args.start_block + ((total_blocks // args.par) * i)),
        (args.start_block + ((total_blocks // args.par) * (i+1)))
    ))
brange[-1] = (brange[-1][0], args.end_block) # fix for last block inclusive

procs = []
for m in brange:
    procs.append(subprocess.Popen([
        "python", "import-block-range-from-leveldb.py",
        "--start-block", str(m[0]),
        "--end-block", str(m[1])
    ]))

for p in procs:
    p.wait()
