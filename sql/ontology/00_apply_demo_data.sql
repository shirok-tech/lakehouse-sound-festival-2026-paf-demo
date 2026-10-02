-- Run as the existing festival data owner (ADB_USER), in a dedicated session.
-- Requires the previous article setup and the corrected Parquet upload.
-- Re-running resets the two ONTOLOGY_DEMO_SEED tasks to OPEN.
WHENEVER OSERROR EXIT FAILURE ROLLBACK
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
SET DEFINE OFF
SET SERVEROUTPUT ON

@@01_check_sources.sql
@@02_create_relation_tables.sql
@@03_seed_relations.sql
@@04_scope_views.sql
@@05_verify_demo_data.sql

PROMPT Ontology demo data preparation completed.
PROMPT Continue with the blog Graph views, integrity checks, Graph and API steps.
SET DEFINE ON
WHENEVER SQLERROR CONTINUE NONE
WHENEVER OSERROR CONTINUE NONE
