import sys
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extras import Json

# this is for python-bitcoin-blockchain-parser to read blocks faster
def build_index_cache(index_path, cache_path, blockchain):
    try:
        open(cache_path, 'r')
        print('found existing cache')
    except FileNotFoundError:
        print('building cache, this may take a long time')

        try:
            for block in blockchain.get_ordered_blocks(
                index=index_path,
                cache=cache_path,
            ):
                break
        except IOError as e:
            print('error parsing blockchain, have you quit bitcoind?')
            print(e)
            sys.exit()

# last block height our index cache has
def count_leveldb_last_block(index_path, cache_path, start, blockchain):
    print('counting up to last block')
    end_block = start 
    for block in blockchain.get_ordered_blocks(
        index=index_path,
        cache=cache_path,
        start=start
    ):
        end_block += 1

    print('end_block found: {}'.format(end_block))
    return end_block


def meta_get_last_block_height(db):
    last_block = db.meta.find_one({
        'column': 'last_block'
    }, {
        'height': 1
    })

    if last_block is not None:
        return last_block['height']

    return None

def meta_update_last_block_height(db, height):
    db.meta.update({
        'column': 'last_block'
    }, {
        'column': 'last_block',
        "height": height
    }, upsert=True)

# returns amount deleted
def delete_txs_gte(db, height):
    return db.confirmed.delete_many({
        'blk.i': {
            '$gte': height
        }
    }).deleted_count

def insert_documents(cur, documents):
    txs_q  = 'INSERT INTO bitdb.txs (txid, height, blockhash) VALUES %s'
    vin_q  = 'INSERT INTO bitdb.vin (txid, height, prevout_txid, prevout_vout, sender, tna) VALUES %s'
    vout_q = 'INSERT INTO bitdb.vout (txid, height, n, satoshis, receiver, tna) VALUES %s'

    txs_b  = []
    vin_b  = []
    vout_b = []

    for d in documents:
        txs_b.append((d['tx']['h'], d['blk']['i'], d['blk']['h']))
        for i in d['in']:
            vin_b.append((d['tx']['h'], d['blk']['i'], i['e']['h'], i['e']['i'], i['e']['a'], Json(i['tna'])))
        for i in d['out']:
            vout_b.append((d['tx']['h'], d['blk']['i'], i['e']['i'], i['e']['v'], i['e']['a'], Json(i['tna'])))


    execute_values(cur, txs_q, txs_b)
    execute_values(cur, vin_q, vin_b)
    execute_values(cur, vout_q, vout_b)

    print("inserted {} documents".format(len(documents)))
