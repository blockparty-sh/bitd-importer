-- Deploy bitdb:blocks to pg
-- requires: appschema

BEGIN;

CREATE TABLE bitdb.blocks (
    height      INTEGER         PRIMARY KEY,
    hash        VARCHAR(32)     NOT NULL,
    timestamp   INTEGER         NOT NULL
);

CREATE INDEX idx_blocks_height ON bitdb.blocks USING btree (height);
CREATE INDEX idx_blocks_hash ON bitdb.blocks USING btree (hash);
CREATE INDEX idx_blocks_timestamp ON bitdb.blocks USING btree (timestamp);

COMMIT;
