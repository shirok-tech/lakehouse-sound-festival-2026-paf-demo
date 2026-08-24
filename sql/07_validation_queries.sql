-- Expected: Waveform Arena has the largest Day 2 delay and INC-2026-081 affects three performances.
SELECT * FROM V_STAGE_DELAY_ANALYSIS
WHERE FESTIVAL_DATE = '2026-08-08'
ORDER BY DELAY_MINUTES DESC FETCH FIRST 10 ROWS ONLY;

-- Expected: EQ-NET-WA-01 shows high temperature, packet loss and low fan RPM.
SELECT * FROM V_EQUIPMENT_HEALTH_SUMMARY
WHERE EQUIPMENT_ID = 'EQ-NET-WA-01'
ORDER BY METRIC_NAME;

-- Expected: Gate C has a much higher failure rate and queue estimate on Day 2.
SELECT * FROM V_GATE_CONGESTION_ANALYSIS
WHERE FESTIVAL_DATE = '2026-08-08'
ORDER BY GATE_ID, RESULT_CODE;

-- Expected: Lunar Echo hoodie planned stock 420 versus interest-adjusted forecast 690.
SELECT * FROM V_MERCH_STOCKOUT_ANALYSIS
WHERE PRODUCT_ID = 'MER-LUN-HOOD-BLK-M';

-- Validate external table files after creation.
BEGIN
  DBMS_CLOUD.VALIDATE_EXTERNAL_TABLE(table_name => 'EXT_TICKET_SALES');
  DBMS_CLOUD.VALIDATE_EXTERNAL_TABLE(table_name => 'EXT_ADMISSION_LOGS');
  DBMS_CLOUD.VALIDATE_EXTERNAL_TABLE(table_name => 'EXT_EQUIPMENT_SENSOR_LOGS');
END;
/
