# install system deps

sudo apt-get install libleveldb-dev screen

# setup virtualenv and install python deps

virtualenv venv --python python3
source venv/bin/activate
pip install -r requirements.txt


# install blockchain-parser

cd python-bitcoin-blockchain-parser
python setup.py install

# patch python-bitcoinlib because it will give error for pushdata for some txs

patch venv/lib/python3.5/site-packages/bitcoin/core/script.py patch.txt

# patch bitcoin-abc to add fast mempool transanction rpc

(do this from bitcoin-abc directory)

git am < 0001-Add-new-RPC-call-getrawmempooltxs.patch
make
(make install?)

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
# this will import from leveldb and in parallel
# only run this once, the start_bitd.sh script will keep you updated
python import.py --start-block 558000 --par 4
# start bitcoin again
bitcoind -daemon
# this will run the rpc, mempool, and zmq scripts
# it is recommended to add this to start running after bitcoind
# starts on your machine
bash start_bitd.sh 

# open screen to see status of zmq listener
screen -r bitd-importer
