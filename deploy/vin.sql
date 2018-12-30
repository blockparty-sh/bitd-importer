-- Deploy bitdb:vin to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.vin (
    txid        VARCHAR(32)     NOT NULL,
    vout        INTEGER         NOT NULL,
    sender      VARCHAR(42)     NOT NULL,
    tna         JSONB           NOT NULL
);

CREATE INDEX idx_vin_txid ON bitdb.vin USING btree (txid);
CREATE INDEX idx_vin_vout ON bitdb.vin USING btree (vout);
CREATE INDEX idx_vin_sender ON bitdb.vin USING btree (sender);
CREATE INDEX idx_vin_tna ON bitdb.vin USING gin (tna);

COMMIT;
