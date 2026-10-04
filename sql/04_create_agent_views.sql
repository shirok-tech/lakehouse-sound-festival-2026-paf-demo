CREATE OR REPLACE VIEW V_STAGE_DELAY_ANALYSIS AS
SELECT
  s.festival_date,
  s.stage_id,
  st.stage_name,
  s.performance_id,
  s.artist_name,
  s.planned_start_ts,
  a.actual_start_ts,
  a.delay_minutes,
  a.status,
  a.incident_id
FROM ext_performance_schedule s
JOIN ext_performance_actual a ON a.performance_id = s.performance_id
LEFT JOIN ext_stages st ON st.stage_id = s.stage_id;

CREATE OR REPLACE VIEW V_EQUIPMENT_HEALTH_SUMMARY AS
SELECT
  festival_date,
  stage_id,
  equipment_id,
  metric_name,
  ROUND(AVG(metric_value), 3) AS avg_metric_value,
  ROUND(MIN(metric_value), 3) AS min_metric_value,
  ROUND(MAX(metric_value), 3) AS max_metric_value,
  SUM(CASE WHEN status IN ('WARNING','CRITICAL') THEN 1 ELSE 0 END) AS abnormal_event_count
FROM ext_equipment_sensor_logs
GROUP BY festival_date, stage_id, equipment_id, metric_name;

CREATE OR REPLACE VIEW V_GATE_CONGESTION_ANALYSIS AS
SELECT
  festival_date,
  gate_id,
  result_code,
  COUNT(*) AS scan_attempts,
  ROUND(AVG(scan_duration_ms), 1) AS avg_scan_duration_ms,
  ROUND(AVG(queue_estimate_minutes), 1) AS avg_queue_minutes
FROM ext_admission_logs
GROUP BY festival_date, gate_id, result_code;

CREATE OR REPLACE VIEW V_MERCH_STOCKOUT_ANALYSIS AS
SELECT
  p.product_id,
  p.product_name,
  ip.festival_date,
  ip.baseline_forecast_units,
  ip.planned_stock_units,
  ip.interest_adjusted_forecast_units,
  MAX(ms.sale_ts) AS stockout_ts,
  SUM(ms.quantity) AS units_sold
FROM ext_merch_products p
JOIN ext_merch_inventory_plan ip ON ip.product_id = p.product_id
LEFT JOIN ext_merchandise_sales ms ON ms.product_id = p.product_id AND ms.festival_date = ip.festival_date
GROUP BY p.product_id, p.product_name, ip.festival_date, ip.baseline_forecast_units, ip.planned_stock_units, ip.interest_adjusted_forecast_units;

CREATE OR REPLACE VIEW V_REFUND_REQUEST_CONTEXT AS
SELECT
  r.request_id,
  r.ticket_id,
  r.parent_ticket_id,
  r.attendee_id,
  r.reason_code,
  r.requested_amount_jpy,
  t.ticket_type_id,
  t.amount_jpy AS ticket_amount_jpy,
  CASE WHEN EXISTS (
    SELECT 1 FROM ext_admission_logs a
    WHERE a.ticket_id = CASE WHEN r.parent_ticket_id IS NOT NULL AND r.parent_ticket_id <> '' THEN r.parent_ticket_id ELSE r.ticket_id END
      AND a.festival_date = '2026-08-09'
      AND a.result_code = 'SUCCESS'
  ) THEN 1 ELSE 0 END AS day3_admitted_flag
FROM ext_refund_requests r
JOIN ext_ticket_sales t ON t.ticket_id = r.ticket_id;

COMMENT ON TABLE V_STAGE_DELAY_ANALYSIS IS '公演予定と実績を結合し、遅延時間と関連インシデントを分析するAgent向けView';
COMMENT ON TABLE V_EQUIPMENT_HEALTH_SUMMARY IS '機器・指標単位の最小、最大、平均、異常イベント数';
COMMENT ON TABLE V_GATE_CONGESTION_ANALYSIS IS 'ゲート別のスキャン結果、処理時間、待ち時間';
COMMENT ON TABLE V_MERCH_STOCKOUT_ANALYSIS IS '物販計画、関心予測、在庫切れ時刻を比較するView';
COMMENT ON TABLE V_REFUND_REQUEST_CONTEXT IS '払戻申請、チケット種別、Day 3入場有無をまとめたView';
