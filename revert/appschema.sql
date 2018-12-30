-- Revert bitdb:appschema from pg

BEGIN;

    DROP SCHEMA bitdb;

COMMIT;
