-- Revert bitdb:blocks from pg

BEGIN;

DROP TABLE bitdb.blocks;

COMMIT;
