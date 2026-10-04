-- Run as ADB_USER.

-- Extracted from blog v1.3 lines 1353-1365; console output omitted.

COMMENT ON TABLE V_KG_EQUIPMENT IS
  '元Equipment Masterへ出所付きの合成デモLot Relationを重ねたKnowledge Graph用View';

COMMENT ON COLUMN V_KG_EQUIPMENT.MANUFACTURING_LOT IS
  'Graph探索で使用するCanonical Manufacturing Lot';

COMMENT ON COLUMN V_KG_EQUIPMENT.LOT_SOURCE IS
  'Lot関係の出所。MASTER_CSVまたはSYNTHETIC_DEMO';

COMMENT ON TABLE V_KG_TASKS IS
  'Incidentから作成された改善Task。OPENとIN_PROGRESSを未完了として扱う';
