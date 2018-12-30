-- Deploy bitdb:vout to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.vout (
    reftxid     VARCHAR(64)     NOT NULL,
    refheight   INTEGER         NOT NULL,
    n           INTEGER         NOT NULL,
    satoshis    BIGINT          NOT NULL,
    receiver    VARCHAR(42),
    tna         JSONB
);

CREATE INDEX idx_vout_reftxid ON bitdb.vout USING btree (reftxid);
CREATE INDEX idx_vout_refheight ON bitdb.vout USING btree (refheight);
CREATE INDEX idx_vout_n ON bitdb.vout USING btree (n);
CREATE INDEX idx_vout_satoshis ON bitdb.vout USING btree (satoshis);
CREATE INDEX idx_vout_receiver ON bitdb.vout USING btree (receiver);
CREATE INDEX idx_vout_tna ON bitdb.vout USING gin (tna);

COMMIT;
