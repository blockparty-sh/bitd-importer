-- Deploy bitdb:txs to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.txs (
    txid       VARCHAR(64)     PRIMARY KEY,
    height     INTEGER         NOT NULL,
    blockhash  VARCHAR(64)     NOT NULL
);

CREATE INDEX idx_txs_txid ON bitdb.txs USING btree (txid);
CREATE INDEX idx_txs_height ON bitdb.txs USING brin (height);
CREATE INDEX idx_txs_blockhash ON bitdb.txs USING btree (blockhash);

COMMIT;
