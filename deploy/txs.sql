-- Deploy bitdb:txs to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.txs (
    txid        VARCHAR(64)     PRIMARY KEY,
    refheight   INTEGER         NOT NULL,
    refhash     VARCHAR(64)     NOT NULL
);

CREATE INDEX idx_txs_txid ON bitdb.txs USING btree (txid);
CREATE INDEX idx_txs_refheight ON bitdb.txs USING brin (refheight);
CREATE INDEX idx_txs_refhash ON bitdb.txs USING btree (refhash);

COMMIT;
