#!/bin/bash

python tna-render-tx.py --txid $@ > local.txt
python download-tna-from-fountainhead.py --txid $@ > remote.txt
colordiff local.txt remote.txt
