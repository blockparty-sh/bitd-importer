-- Revert bitdb:vout from pg

BEGIN;

DROP TABLE bitdb.vout;

COMMIT;
