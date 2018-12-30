-- Verify bitdb:appschema on pg

BEGIN;

    SELECT pg_catalog.has_schema_privilege('bitdb', 'usage');

ROLLBACK;
