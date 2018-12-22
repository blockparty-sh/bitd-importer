#!/usr/bin/env python3

import os 
import json
import base64
import argparse
import pymongo
from dotenv import load_dotenv
from blockchain_parser.blockchain import Blockchain
from blockchain_parser.address import Address
from bitcoin.core.script import CScriptOp
from cashaddress import convert

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
args = parser.parse_args()

for block in blockchain.get_ordered_blocks(
    index=index_path,
    cache=cache_path,
    start=args.start_block,
    end=args.end_block
):
    #print("height=%d block=%s" % (block.height, block.hash))
    documents = []
    for tx_index, tx in enumerate(block.transactions):
        #print("tx: ", tx)
        #print(tx_index)
        inputs = []
        outputs = []

        for input_index, item in enumerate(tx.inputs):
            xput = { "i": input_index }

            if not tx.is_coinbase(): # coinbase input doesnt have to be valid script
                for chunk_index, chunk in enumerate(item.script.operations):
                    if isinstance(chunk, bytes):
                        xput["b" + str(chunk_index)] = base64.b64encode(chunk).decode("utf-8")
                        xput["h" + str(chunk_index)] = chunk.hex()
                    elif isinstance(chunk, CScriptOp):
                        xput["b" + str(chunk_index)] = { "op": int(chunk) }
                    else:
                        xput["b" + str(chunk_index)] = chunk

            xput["str"] = item.script.value
            sender = {
                "h": item.transaction_hash,
                "i": item.transaction_index,
            }

            addr = None

            # TODO add additional address types
            if not tx.is_coinbase():
                if len(item.script.operations) == 2: # p2pk
                    if len(item.script.operations[1]) == 33:
                        addr = Address.from_public_key(item.script.operations[1]).address

            if addr is not None:
                sender['a'] = convert.to_cash_address(addr)[12:] # remove "bitcoincash:" prefix

            xput["e"] = sender
            inputs.append(xput)

        for output_index, item in enumerate(tx.outputs):
            xput = { "i": output_index }

            for chunk_index, chunk in enumerate(item.script.operations):
                if isinstance(chunk, bytes):
                    xput["b" + str(chunk_index)] = base64.b64encode(chunk).decode("utf-8")
                    try:
                        xput["s" + str(chunk_index)] = chunk.decode("utf-8")
                    except UnicodeDecodeError:
                        pass
                    xput["h" + str(chunk_index)] = chunk.hex()
                elif isinstance(chunk, CScriptOp):
                    xput["b" + str(chunk_index)] = { "op": int(chunk) }
                else:
                    xput["b" + str(chunk_index)] = chunk

            xput["str"] = item.script.value

            receiver = {
                "v": item.value,
                "i": output_index
            }
            # bitdb only supports single address, so we will too
            addresses = [str(m.address) for m in item.addresses]
            if len(addresses) == 1:
                receiver["a"] = convert.to_cash_address(addresses[0])[12:] # remove "bitcoincash:" prefix
            xput["e"] = receiver

            outputs.append(xput)


        d = {
            "tx": { "h": tx.hash },
            "in": inputs,
            "out": outputs,
            "blk": {
                "i": block.height,
                "h": block.hash,
                "t": block.header.timestamp.strftime("%s")
            }
        }
        documents.append(d)
        #print(json.dumps(d, indent=4))
    print("height=%d inserted=%i" % (block.height, len(db.confirmed.insert_many(documents).inserted_ids)))
