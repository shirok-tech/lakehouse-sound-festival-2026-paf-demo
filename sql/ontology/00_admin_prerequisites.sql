-- Run as ADMIN after LSF_AGENT exists. Re-running GRANT is safe.
-- DATA_PUMP_DIR is the database DIRECTORY used by the Parquet external table.
-- The Parquet object itself remains in Object Storage.
GRANT CREATE PROPERTY GRAPH TO ADB_USER;
GRANT READ, WRITE ON DIRECTORY DATA_PUMP_DIR TO ADB_USER;
GRANT CREATE PROCEDURE TO LSF_AGENT;

-- Optional Graph Studio owner login, run as ADMIN only when required:
-- GRANT GRAPH_DEVELOPER TO ADB_USER;
