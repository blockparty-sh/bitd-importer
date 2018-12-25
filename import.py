#!/usr/bin/env python3

import os
import sys
import pymongo
import subprocess
import argparse
from blockchain_parser.blockchain import Blockchain
from dotenv import load_dotenv
import util

load_dotenv()

blocks_path = os.path.expanduser(os.getenv("BLOCKS_PATH"))
index_path  = os.path.expanduser(os.getenv("INDEX_PATH"))
cache_path  = os.path.expanduser(os.getenv("CACHE_PATH"))

parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--start-block", type=int, required=True, help="block to start")
parser.add_argument("--end-block", type=int, help="block to finish on, if not given will get last one in index cache")
parser.add_argument("--par", type=int, required=True, help="amount of processes to divide load between")
parser.add_argument("--dry", action="store_true", help="dry run (no inserts)")
parser.add_argument("--verbose", action="store_true", help="show json from tna")
args = parser.parse_args()

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]

last_block_height = util.meta_get_last_block_height(db)
if not args.dry:
    if last_block_height is not None:
        if args.start_block < last_block_height:
            print('start_block is smaller than last block height in db')
            print("this means you are rescanning parts of the blockchain you've already scanned")
            print("the entries will be deleted, and this is safe, it just might take longer")
            if input("press enter to continue, anything else to exit: ") != "":
                sys.exit()

    if args.start_block-1 > last_block_height:
        print("start_block-1 is greater than last block height in db ({})".format(last_block_height))
        print("this might mean you are skipping blocks")
        if input("press enter to continue, anything else to exit: ") != "":
            sys.exit()


    print('deleted {} txs from gte block {}'.format(
        util.delete_txs_gte(db, args.start_block),
        args.start_block
    ))
    print('deleted {} unconfirmed txs'.format(
        db.unconfirmed.delete_many({}).deleted_count
    ))


blockchain = Blockchain(blocks_path)

util.build_index_cache(index_path, cache_path, blockchain)

if not args.end_block:
    args.end_block = util.count_leveldb_last_block(index_path, cache_path, args.start_block, blockchain)


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
    cmd = [
        "python", "import-block-range-from-leveldb.py",
        "--start-block", str(m[0]),
        "--end-block", str(m[1])
    ]

    if args.dry:
        cmd.append("--dry")

    if args.verbose:
        cmd.append("--verbose")

    procs.append(subprocess.Popen(cmd))

for p in procs:
    p.wait()

if not args.dry:
    util.meta_update_last_block_height(db, args.end_block)
