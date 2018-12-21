# install system deps

sudo apt-get install libleveldb-dev

# setup virtualenv and install python deps

virtualenv venv --python python3
source venv/bin/activate
pip install -r requirements.txt


# install blockchain-parser

git pull -X theirs -s subtree https://github.com/alecalve/python-bitcoin-blockchain-parser master
cd python-bitcoin-blockchain-parser
python setup.py install

# patch python-bitcoinlib because it will give error for pushdata for some txs

patch venv/lib/python3.5/site-packages/python_bitcoinlib-0.5.0-py3.5.egg/bitcoin/core/script.py patch.txt

# stop bitcoind at this point, so the lock on leveldb is removed

bitcoin-cli stop

# edit configuration

cp .env.example .env
vim .env

# run import (make sure mongodb is running)

python import.py
