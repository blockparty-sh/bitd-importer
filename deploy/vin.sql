-- Deploy bitdb:vin to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.vin (
    reftxid     VARCHAR(64)     NOT NULL,
    refheight   INTEGER         NOT NULL,
    txid        VARCHAR(64)     NOT NULL,
    vout        INTEGER         NOT NULL,
    sender      VARCHAR(42),
    tna         JSONB
);

CREATE INDEX idx_vin_reftxid ON bitdb.vin USING btree (reftxid);
CREATE INDEX idx_vin_refheight ON bitdb.vin USING btree (refheight);
CREATE INDEX idx_vin_txid ON bitdb.vin USING btree (txid);
CREATE INDEX idx_vin_vout ON bitdb.vin USING btree (vout);
CREATE INDEX idx_vin_sender ON bitdb.vin USING btree (sender);
CREATE INDEX idx_vin_tna ON bitdb.vin USING gin (tna);

COMMIT;
