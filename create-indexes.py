#!/usr/bin/env python3

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]

def add_indexes_to_collection(collection):
    print('dropping old indexes')
    collection.drop_indexes();

    print('adding tx.h')
    collection.create_index("tx.h", unique=True)

    print('adding blk.i')
    collection.create_index("blk.i")
    print('adding blk.h')
    collection.create_index("blk.h")
    print('adding blk.t')
    collection.create_index("blk.t")

    print('adding in.e.i')
    collection.create_index("in.e.i")
    print('adding in.e.a')
    collection.create_index("in.e.a")
    print('adding in.e.h')
    collection.create_index("in.e.h")
    print('adding in.i')
    collection.create_index("in.i")

    print('adding out.e.a')
    collection.create_index("out.e.a")
    print('adding out.e.v')
    collection.create_index("out.e.v")
    print('adding out.e.i')
    collection.create_index("out.e.i")
    print('adding out.i')
    collection.create_index("out.i")

    for i in range(0, 8):
        print('adding in.h{}'.format(i))
        collection.create_index("in.h"+str(i))

        print('adding in.b{}'.format(i))
        collection.create_index("in.b"+str(i))

        print('adding out.s'.format(i))
        collection.create_index("out.s"+str(i))
        print('adding out.s{} (FULLTEXT)'.format(i))
        #collection.drop_index("out.s"+str(i)+"_text")
        #collection.create_index([("out.s"+str(i), pymongo.TEXT)])
        print('adding out.h{}'.format(i))
        collection.create_index("out.h"+str(i))
        print('adding out.b{}'.format(i))
        collection.create_index("out.b"+str(i))

print('CONFIRMED')
add_indexes_to_collection(db.confirmed)
print('UNCONFIRMED')
add_indexes_to_collection(db.unconfirmed)
