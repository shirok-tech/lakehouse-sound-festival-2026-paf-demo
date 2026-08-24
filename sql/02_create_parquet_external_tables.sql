-- Parquet external tables. DBMS_CLOUD derives columns from file metadata.
BEGIN
  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_TICKET_SALES',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/ticket_sales/ticket_sales.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_ADMISSION_LOGS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/admission_logs/year=2026/month=08/day=07/part-000.parquet,&OBJ_URI/data/parquet/admission_logs/year=2026/month=08/day=08/part-000.parquet,&OBJ_URI/data/parquet/admission_logs/year=2026/month=08/day=09/part-000.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_PERFORMANCE_SCHEDULE',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/performances/performance_schedule.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_PERFORMANCE_ACTUAL',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/performances/performance_actual.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_EQUIPMENT_SENSOR_LOGS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/equipment_sensor_logs/year=2026/month=08/day=07/part-000.parquet,&OBJ_URI/data/parquet/equipment_sensor_logs/year=2026/month=08/day=08/part-000.parquet,&OBJ_URI/data/parquet/equipment_sensor_logs/year=2026/month=08/day=09/part-000.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_EQUIPMENT_MAINTENANCE',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/equipment_maintenance/equipment_maintenance.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_INCIDENTS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/incidents/incidents.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_MERCHANDISE_SALES',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/merchandise_sales/year=2026/month=08/day=07/part-000.parquet,&OBJ_URI/data/parquet/merchandise_sales/year=2026/month=08/day=08/part-000.parquet,&OBJ_URI/data/parquet/merchandise_sales/year=2026/month=08/day=09/part-000.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_INVENTORY_SNAPSHOTS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/inventory_snapshots/year=2026/month=08/day=07/part-000.parquet,&OBJ_URI/data/parquet/inventory_snapshots/year=2026/month=08/day=08/part-000.parquet,&OBJ_URI/data/parquet/inventory_snapshots/year=2026/month=08/day=09/part-000.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_WEATHER_OBSERVATIONS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/weather_observations/year=2026/month=08/day=07/part-000.parquet,&OBJ_URI/data/parquet/weather_observations/year=2026/month=08/day=08/part-000.parquet,&OBJ_URI/data/parquet/weather_observations/year=2026/month=08/day=09/part-000.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );

  DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
    table_name      => 'EXT_REFUND_REQUESTS',
    credential_name => '&CRED_NAME',
    file_uri_list   => '&OBJ_URI/data/parquet/refund_requests/refund_requests.parquet',
    format          => '{"type":"parquet","schema":"first"}'
  );
END;
/
