-- Deploy bitdb:vin to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.vin (
    txid          VARCHAR(64)     NOT NULL,
    height        INTEGER         NOT NULL,
    prevout_txid  VARCHAR(64)     NOT NULL,
    prevout_vout  INTEGER         NOT NULL,
    sender        VARCHAR(42),
    tna           JSONB
);

CREATE INDEX idx_vin_txid ON bitdb.vin USING btree (txid);
CREATE INDEX idx_vin_height ON bitdb.vin USING btree (height);
CREATE INDEX idx_vin_prevout_txid ON bitdb.vin USING btree (prevout_txid);
CREATE INDEX idx_vin_prevout_vout ON bitdb.vin USING btree (prevout_vout);
CREATE INDEX idx_vin_sender ON bitdb.vin USING btree (sender);
CREATE INDEX idx_vin_tna ON bitdb.vin USING gin (tna);

COMMIT;
