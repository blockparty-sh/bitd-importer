#!/usr/bin/env python3

import os 
import json
import base64
import argparse
import binascii
from dotenv import load_dotenv
from blockchain_parser.block import Block
from blockchain_parser.transaction import Transaction
import bitcoin.rpc
import tna

load_dotenv()

btc_conf_file = os.path.expanduser(os.getenv("BTC_CONF_FILE"))

parser = argparse.ArgumentParser(description="render a tx with tna")
parser.add_argument("--txid", type=str, required=True, help="txid to look up")
args = parser.parse_args()

rpc = bitcoin.rpc.RawProxy(btc_conf_file=btc_conf_file)

raw_tx_json = rpc.getrawtransaction(args.txid, 1)

raw_block_json = rpc.getblock(raw_tx_json['blockhash'])
raw_block = binascii.unhexlify(rpc.getblock(raw_tx_json['blockhash'], False))
block = Block(raw_block, raw_block_json['height'])

tx = Transaction.from_hex(binascii.unhexlify(raw_tx_json['hex']))
res = tna.extract(block, tx)
print(json.dumps(res, sort_keys=True, indent=4))
