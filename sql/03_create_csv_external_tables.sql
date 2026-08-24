-- CSV master and planning tables. Column lists are explicit for predictable types.
BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_STAGES',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/csv/master/stages.csv',
    column_list     => 'STAGE_ID VARCHAR2(20), STAGE_NAME VARCHAR2(100), STAGE_TYPE VARCHAR2(40), CAPACITY NUMBER, LOCATION_ZONE VARCHAR2(100), NETWORK_ZONE VARCHAR2(20), WEATHER_EXPOSED_FLAG NUMBER',
    format          => '{"type":"csv","skipheaders":1,"delimiter":",","quote":"\"","rejectlimit":"unlimited"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_EQUIPMENT_MASTER',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/csv/master/equipment_master.csv',
    column_list     => 'EQUIPMENT_ID VARCHAR2(40), STAGE_ID VARCHAR2(20), EQUIPMENT_CATEGORY VARCHAR2(40), MODEL_NAME VARCHAR2(100), SERIAL_NUMBER VARCHAR2(40), MANUFACTURING_LOT VARCHAR2(40), VENDOR_ID VARCHAR2(20), FIRMWARE_VERSION VARCHAR2(20), INSTALLED_DATE VARCHAR2(10), CRITICALITY VARCHAR2(20)',
    format          => '{"type":"csv","skipheaders":1,"delimiter":",","quote":"\"","rejectlimit":"unlimited"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_MERCH_PRODUCTS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/csv/master/merchandise_products.csv',
    column_list     => 'PRODUCT_ID VARCHAR2(50), PRODUCT_NAME VARCHAR2(200), ARTIST_ID VARCHAR2(20), CATEGORY VARCHAR2(40), UNIT_PRICE_JPY NUMBER, INITIAL_STOCK_DAY1 NUMBER, INITIAL_STOCK_DAY2 NUMBER, INITIAL_STOCK_DAY3 NUMBER, VENDOR_ID VARCHAR2(20), ACTIVE_FLAG NUMBER',
    format          => '{"type":"csv","skipheaders":1,"delimiter":",","quote":"\"","rejectlimit":"unlimited"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_MERCH_INVENTORY_PLAN',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/csv/transactions/merch_inventory_plan.csv',
    column_list     => 'PRODUCT_ID VARCHAR2(50), FESTIVAL_DATE VARCHAR2(10), BASELINE_FORECAST_UNITS NUMBER, INTEREST_ADJUSTED_FORECAST_UNITS NUMBER, PLANNED_STOCK_UNITS NUMBER, FORECAST_METHOD_USED VARCHAR2(40), PLANNING_NOTE VARCHAR2(200)',
    format          => '{"type":"csv","skipheaders":1,"delimiter":",","quote":"\"","rejectlimit":"unlimited"}'
  );
END;
/
