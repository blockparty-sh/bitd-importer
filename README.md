# install system deps

sudo apt-get install libleveldb-dev

# setup virtualenv and install python deps

virtualenv venv --python python3
source venv/bin/activate
pip install -r requirements.txt


# install blockchain-parser

cd python-bitcoin-blockchain-parser
python setup.py install

# patch python-bitcoinlib because it will give error for pushdata for some txs

patch venv/lib/python3.5/site-packages/bitcoin/core/script.py

# edit bitcoin configuration

vim ~/.bitcoin/bitcoin.conf

server=1
rpcallowip=0.0.0.0/0
rpcport=8332
rpcuser=root
rpcpassword=bitcoin
txindex=1
zmqpubrawtx=tcp://127.0.0.1:28332
zmqpubrawblock=tcp://127.0.0.1:28332


# edit configuration

cp .env.example .env
vim .env

set values to match bitcoin configuration

# stop bitcoind at this point, so the lock on leveldb is removed

bitcoin-cli stop
# run import (make sure mongodb is running)

python import.py --start-block 558000 --end-block 559000 --par 4
