-- Run as ADB_USER on a new environment; do not rerun against existing external tables.
@@00_variables.sql
@@02_create_parquet_external_tables.sql
@@03_create_csv_external_tables.sql
@@04_create_agent_views.sql
@@07_validation_queries.sql
PROMPT Owner-side base views complete. Create the runtime user and action table in separate user sessions as documented in README.md.
