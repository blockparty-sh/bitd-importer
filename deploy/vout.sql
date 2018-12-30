-- Deploy bitdb:vout to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.vout (
    txid        VARCHAR(64)     NOT NULL,
    height      INTEGER         NOT NULL,
    n           INTEGER         NOT NULL,
    satoshis    BIGINT          NOT NULL,
    receiver    VARCHAR(42),
    tna         JSONB
);

CREATE INDEX idx_vout_txid ON bitdb.vout USING btree (txid);
CREATE INDEX idx_vout_height ON bitdb.vout USING btree (height);
CREATE INDEX idx_vout_n ON bitdb.vout USING btree (n);
CREATE INDEX idx_vout_satoshis ON bitdb.vout USING btree (satoshis);
CREATE INDEX idx_vout_receiver ON bitdb.vout USING btree (receiver);
CREATE INDEX idx_vout_tna ON bitdb.vout USING gin (tna);

COMMIT;
