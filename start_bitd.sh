#!/bin/bash

source venv/bin/activate

python import-block-range-from-rpc.py || exit
screen -S bitd-importer -d -m python import-from-zmq.py 
python import-txs-from-mempool.py || exit
