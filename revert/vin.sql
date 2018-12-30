-- Revert bitdb:vin from pg

BEGIN;

DROP TABLE bitdb.vin;

COMMIT;
