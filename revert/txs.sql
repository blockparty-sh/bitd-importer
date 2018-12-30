-- Revert bitdb:txs from pg

BEGIN;

DROP TABLE bitdb.txs;

COMMIT;
