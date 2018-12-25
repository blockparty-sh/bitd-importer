import sys

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

