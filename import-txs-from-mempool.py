#!/usr/bin/env python3

import os 
import json
import base64
import argparse
import binascii
import pymongo
from dotenv import load_dotenv
from blockchain_parser.transaction import Transaction
import bitcoin.rpc
import tna

load_dotenv()

btc_conf_file = os.path.expanduser(os.getenv("BTC_CONF_FILE"))


parser = argparse.ArgumentParser(description="import transactions to bitdb")
parser.add_argument("--dry", action="store_true", help="dry run (no inserts)")
parser.add_argument("--verbose", action="store_true", help="show json from tna")
args = parser.parse_args()

rpc = bitcoin.rpc.RawProxy(btc_conf_file=btc_conf_file)

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]

if not args.dry:
    print('deleted {} txs from unconfirmed'.format(
        db.unconfirmed.delete_many({}).deleted_count
    ))

documents = []
transactions = rpc.getrawmempooltxs()
total_transactions = len(transactions)
for txdata_index, txdata in enumerate(transactions):
    tx = Transaction.from_hex(binascii.unhexlify(txdata))
    res = tna.extract(None, tx)
    if args.verbose:
        print(json.dumps(res, indent=4))
    documents.append(res)

    print("{}%\t{}/{}".format(
        round((txdata_index / total_transactions) * 100, 2),
        txdata_index,
        total_transactions
    ))

if not args.dry:
    inserted = len(db.unconfirmed.insert_many(documents).inserted_ids)
    print("inserted={}".format(inserted))
