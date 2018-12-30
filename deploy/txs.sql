-- Deploy bitdb:txs to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.txs (
    txid        VARCHAR(32)     PRIMARY KEY,
    blockhash   VARCHAR(32)     NOT NULL,
    blockid     INTEGER         NOT NULL
);

CREATE INDEX idx_txs_txid ON bitdb.txs USING btree (txid);
CREATE INDEX idx_txs_blockhash ON bitdb.txs USING btree (blockhash);
CREATE INDEX idx_txs_blockid ON bitdb.txs USING brin (blockid);

COMMIT;
