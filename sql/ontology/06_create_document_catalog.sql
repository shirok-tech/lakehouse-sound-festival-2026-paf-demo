-- Run as ADB_USER after @sql/00_variables.sql and uploading metadata/document_catalog.csv.
-- The previous article does not create this external table. Reuses an existing table.
DECLARE
  L_COUNT PLS_INTEGER;
BEGIN
  SELECT COUNT(*) INTO L_COUNT FROM USER_TABLES
  WHERE TABLE_NAME = 'EXT_DOCUMENT_CATALOG';
  IF L_COUNT = 0 THEN
    DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
      table_name      => 'EXT_DOCUMENT_CATALOG',
      credential_name => '&CRED_NAME',
      file_uri_list   => '&OBJ_URI/metadata/document_catalog.csv',
      column_list     => 'DOCUMENT_ID VARCHAR2(40),
                          FILE_NAME VARCHAR2(255),
                          DOCUMENT_TYPE VARCHAR2(80),
                          VERSION VARCHAR2(20),
                          EFFECTIVE_DATE VARCHAR2(10),
                          PURPOSE VARCHAR2(500)',
      format          => '{"type":"csv","skipheaders":1,"delimiter":",","quote":"\"","rejectlimit":"unlimited"}'
    );
  END IF;
END;
/

-- Confirm the existing table points to the uploaded catalog, then inspect names.
SELECT TABLE_NAME, LOCATION FROM USER_EXTERNAL_LOCATIONS
WHERE TABLE_NAME = 'EXT_DOCUMENT_CATALOG';
SELECT DOCUMENT_ID, FILE_NAME, VERSION FROM EXT_DOCUMENT_CATALOG
ORDER BY DOCUMENT_ID;
