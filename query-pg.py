#!/usr/bin/env python3

import os 
import argparse
import json
import psycopg2
from dotenv import load_dotenv
from blockchain_parser.blockchain import Blockchain
import util

load_dotenv()

conn = psycopg2.connect(user=os.getenv("POSTGRES_USER"),
                        password=os.getenv("POSTGRES_PASSWORD"),
                        database=os.getenv("POSTGRES_DB"))
cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)


parser = argparse.ArgumentParser(description="query database, get json")
parser.add_argument("--query", type=str, required=True, help="query")
args = parser.parse_args()

cur.execute(args.query);
res = []
row = cur.fetchone()
while row:
    res.append(row._asdict())
    row = cur.fetchone()
print(json.dumps(res, indent=4))

cur.close()
conn.close()
