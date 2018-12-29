#!/usr/bin/env python3

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

mongo = pymongo.MongoClient(os.getenv('MONGO_URL'))
db = mongo[os.getenv('MONGO_NAME')]

def add_indexes_to_collection(collection):
    print('adding blk.i')
    collection.create_index("blk.i")
    print('adding blk.h')
    collection.create_index("blk.h")
    print('adding blk.t')
    collection.create_index("blk.t")
    print('adding tx.h')
    collection.create_index("tx.h")

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

    for i in range(0, 16):
        print('adding in.h1', i)
        collection.create_index("in.h"+str(i))
        print('adding in.b1', i)
        collection.create_index("in.b"+str(i))

        print('adding out.s1', i)
        collection.create_index("out.s"+str(i))
        print('adding out.s1 (FULLTEXT)', i)
        collection.create_index([("out.s"+str(i), pymongo.TEXT)])
        print('adding out.h1', i)
        collection.create_index("out.h"+str(i))
        print('adding out.b1', i)
        collection.create_index("out.b"+str(i))

print('CONFIRMED')
add_indexes_to_collection(db.confirmed)
print('UNCONFIRMED')
add_indexes_to_collection(db.unconfirmed)
