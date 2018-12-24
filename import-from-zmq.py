#!/usr/bin/env python3
# Copyright (c) 2014-2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import binascii
import asyncio
import zmq
import zmq.asyncio
import signal
import struct
import os 
import sys
import json
import pymongo
from dotenv import load_dotenv
from blockchain_parser.transaction import Transaction
from blockchain_parser.block import Block
import bitcoin.rpc
import tna



load_dotenv()

btc_conf_file = os.path.expanduser(os.getenv("BTC_CONF_FILE"))
zmq_url = os.getenv('ZMQ_URL')

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]

rpc = bitcoin.rpc.RawProxy(btc_conf_file=btc_conf_file)

# this will be incremented when a new block comes
current_block_count = rpc.getblockcount()

class ZMQHandler():
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.zmqContext = zmq.asyncio.Context()

        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)
        self.zmqSubSocket.setsockopt(zmq.RCVHWM, 0)
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "rawblock")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "rawtx")
        self.zmqSubSocket.connect(zmq_url)

    async def handle(self):
        global current_block_count

        msg = await self.zmqSubSocket.recv_multipart()
        topic = msg[0]
        body = msg[1]
        sequence = "Unknown"

        if len(msg[-1]) == 4:
            msgSequence = struct.unpack('<I', msg[-1])[-1]
            sequence = str(msgSequence)
        
        if topic == b"rawblock":
            try:
                block = Block(body, current_block_count+1)
                current_block_count += 1

                documents = []
                d_txids = []
                for tx in block.transactions:
                    res = tna.extract(block, tx)
                    #print(json.dumps(res, indent=4))
                    documents.append(res)
                    d_txids.append(tx.hash)

                print("height={} inserted={}".format(
                    block.height,
                    len(db.confirmed.insert_many(documents).inserted_ids)
                ))

                for txid in d_txids:
                    db.unconfirmed.delete_one({
                        'tx': { 'h': txid }
                    })
            except AssertionError:
                print('error: rawblock')

        elif topic == b"rawtx":
            try:
                tx = Transaction.from_hex(body)
                res = tna.extract(None, tx)
                db.unconfirmed.insert_one(res)
                print('inserted tx: {}'.format(tx.hash))
            except:
                print('error: rawtx')
        # schedule to receive next message
        asyncio.ensure_future(self.handle())

    def start(self):
        self.loop.add_signal_handler(signal.SIGINT, self.stop)
        self.loop.create_task(self.handle())
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
        self.zmqContext.destroy()

daemon = ZMQHandler()
daemon.start()
