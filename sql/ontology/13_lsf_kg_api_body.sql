-- Run as ADB_USER.

-- Extracted from blog v1.3 lines 2331-2598; console output omitted.

CREATE OR REPLACE PACKAGE BODY LSF_KG_API AS
  PROCEDURE ASSERT_INCIDENT_ID (P_INCIDENT_ID IN VARCHAR2) AS
    L_COUNT PLS_INTEGER;
  BEGIN
    IF P_INCIDENT_ID IS NULL
       OR NOT REGEXP_LIKE(P_INCIDENT_ID, '^INC-[0-9A-Z-]{1,24}$') THEN
      RAISE_APPLICATION_ERROR(-20011, 'Invalid Incident ID');
    END IF;
    SELECT COUNT(*)
      INTO L_COUNT
      FROM V_KG_INCIDENTS
     WHERE INCIDENT_ID = P_INCIDENT_ID;
    IF L_COUNT = 0 THEN
      RAISE_APPLICATION_ERROR(-20012, 'Incident ID was not found');
    ELSIF L_COUNT > 1 THEN
      RAISE_APPLICATION_ERROR(-20013, 'Duplicate Incident ID');
    END IF;
  END ASSERT_INCIDENT_ID;
  PROCEDURE GET_INCIDENT_IMPACT (
    P_INCIDENT_ID IN  VARCHAR2,
    P_RESULT      OUT CLOB
  ) AS
  BEGIN
    ASSERT_INCIDENT_ID(P_INCIDENT_ID);
    SELECT JSON_ARRAYAGG(
             JSON_OBJECT(
               'incident_id'          VALUE INCIDENT_ID,
               'affected_equipment_id' VALUE AFFECTED_EQUIPMENT_ID,
               'manufacturing_lot'     VALUE MANUFACTURING_LOT,
               'related_equipment_id'  VALUE RELATED_EQUIPMENT_ID,
               'related_stage_id'      VALUE RELATED_STAGE_ID,
               'related_stage_name'    VALUE RELATED_STAGE_NAME,
               'lot_source'            VALUE LOT_SOURCE,
               'lot_assertion_status'  VALUE LOT_ASSERTION_STATUS,
               'lot_source_reference_id' VALUE LOT_SOURCE_REFERENCE_ID,
               'affected_lot_source' VALUE AFFECTED_LOT_SOURCE,
               'affected_lot_assertion_status' VALUE AFFECTED_LOT_ASSERTION_STATUS,
               'affected_lot_source_reference_id' VALUE AFFECTED_LOT_SOURCE_REFERENCE_ID
             )
             ORDER BY RELATED_STAGE_ID, RELATED_EQUIPMENT_ID
             RETURNING CLOB
           )
      INTO P_RESULT
      FROM GRAPH_TABLE (
        LSF_FESTIVAL_OPS_GRAPH
        MATCH
          (I IS INCIDENT)
            -[A IS AFFECTS]->
          (E1 IS EQUIPMENT)
            -[B1 IS BELONGS_TO_LOT]->
          (L IS MANUFACTURING_LOT)
            <-[B2 IS BELONGS_TO_LOT]-
          (E2 IS EQUIPMENT)
            -[D IS DEPLOYED_AT]->
          (S IS STAGE)
        WHERE E1.EQUIPMENT_ID <> E2.EQUIPMENT_ID
        COLUMNS (
          I.INCIDENT_ID       AS INCIDENT_ID,
          E1.EQUIPMENT_ID     AS AFFECTED_EQUIPMENT_ID,
          L.MANUFACTURING_LOT AS MANUFACTURING_LOT,
          E2.EQUIPMENT_ID     AS RELATED_EQUIPMENT_ID,
          S.STAGE_ID          AS RELATED_STAGE_ID,
          S.STAGE_NAME        AS RELATED_STAGE_NAME,
          B2.LOT_SOURCE       AS LOT_SOURCE,
          B2.LOT_ASSERTION_STATUS AS LOT_ASSERTION_STATUS,
          B2.LOT_SOURCE_REFERENCE_ID AS LOT_SOURCE_REFERENCE_ID,
          B1.LOT_SOURCE AS AFFECTED_LOT_SOURCE,
          B1.LOT_ASSERTION_STATUS AS AFFECTED_LOT_ASSERTION_STATUS,
          B1.LOT_SOURCE_REFERENCE_ID AS AFFECTED_LOT_SOURCE_REFERENCE_ID
        )
      ) G
     WHERE G.INCIDENT_ID = P_INCIDENT_ID;
    IF P_RESULT IS NULL THEN
      P_RESULT := TO_CLOB('[]');
    END IF;
  END GET_INCIDENT_IMPACT;
  PROCEDURE GET_OPEN_TASKS (
    P_INCIDENT_ID IN  VARCHAR2,
    P_RESULT      OUT CLOB
  ) AS
  BEGIN
    ASSERT_INCIDENT_ID(P_INCIDENT_ID);
    SELECT JSON_ARRAYAGG(
             JSON_OBJECT(
               'incident_id' VALUE INCIDENT_ID,
               'task_id'     VALUE TASK_ID,
               'task_code'   VALUE TASK_CODE,
               'priority'    VALUE PRIORITY,
               'status'      VALUE TASK_STATUS,
               'equipment_id' VALUE EQUIPMENT_ID,
               'stage_id'     VALUE STAGE_ID,
               'stage_name'   VALUE STAGE_NAME,
               'created_by_agent' VALUE CREATED_BY_AGENT,
               'source_type' VALUE SOURCE_TYPE,
               'source_reference_id' VALUE SOURCE_REFERENCE_ID
             )
             ORDER BY
               CASE PRIORITY
                 WHEN 'CRITICAL' THEN 1
                 WHEN 'HIGH'     THEN 2
                 WHEN 'MEDIUM'   THEN 3
                 WHEN 'LOW'      THEN 4
                 ELSE 5
               END,
               TASK_ID
             RETURNING CLOB
           )
      INTO P_RESULT
      FROM GRAPH_TABLE (
        LSF_FESTIVAL_OPS_GRAPH
        MATCH
          (I IS INCIDENT)
            -[C IS CREATES]->
          (T IS TASK)
            -[X IS TARGETS]->
          (E IS EQUIPMENT)
            -[D IS DEPLOYED_AT]->
          (S IS STAGE)
        WHERE T.STATUS IN ('OPEN', 'IN_PROGRESS')
        COLUMNS (
          I.INCIDENT_ID  AS INCIDENT_ID,
          T.TASK_ID      AS TASK_ID,
          T.TASK_CODE    AS TASK_CODE,
          T.PRIORITY     AS PRIORITY,
          T.STATUS       AS TASK_STATUS,
          E.EQUIPMENT_ID AS EQUIPMENT_ID,
          S.STAGE_ID     AS STAGE_ID,
          S.STAGE_NAME   AS STAGE_NAME,
          T.CREATED_BY_AGENT AS CREATED_BY_AGENT,
          X.SOURCE_TYPE AS SOURCE_TYPE,
          X.SOURCE_REFERENCE_ID AS SOURCE_REFERENCE_ID
        )
      ) G
     WHERE G.INCIDENT_ID = P_INCIDENT_ID;
    IF P_RESULT IS NULL THEN
      P_RESULT := TO_CLOB('[]');
    END IF;
  END GET_OPEN_TASKS;
  PROCEDURE GET_RELATED_DOCUMENTS (
    P_INCIDENT_ID IN  VARCHAR2,
    P_RESULT      OUT CLOB
  ) AS
  BEGIN
    ASSERT_INCIDENT_ID(P_INCIDENT_ID);
    SELECT JSON_ARRAYAGG(
             JSON_OBJECT(
               'document_id' VALUE DOCUMENT_ID,
               'file_name' VALUE FILE_NAME,
               'document_type' VALUE DOCUMENT_TYPE,
               'document_version' VALUE DOCUMENT_VERSION,
               'effective_date' VALUE EFFECTIVE_DATE,
               'incident_id' VALUE INCIDENT_ID,
               'equipment_id' VALUE EQUIPMENT_ID,
               'manufacturing_lot' VALUE MANUFACTURING_LOT,
               'task_id' VALUE TASK_ID,
               'task_created_by_agent' VALUE TASK_CREATED_BY_AGENT,
               'relation_type' VALUE RELATION_TYPE,
               'path' VALUE PATH,
               'source_type' VALUE SOURCE_TYPE,
               'source_reference_id' VALUE SOURCE_REFERENCE_ID,
               'lot_source' VALUE LOT_SOURCE,
               'lot_source_reference_id' VALUE LOT_SOURCE_REFERENCE_ID
               NULL ON NULL
               RETURNING CLOB
             )
             ORDER BY DOCUMENT_ID, RELATION_TYPE, TASK_ID
             RETURNING CLOB
           )
      INTO P_RESULT
      FROM (
        SELECT *
        FROM GRAPH_TABLE (
          LSF_FESTIVAL_OPS_GRAPH
          MATCH
            (I IS INCIDENT)
              -[R IS DOCUMENTED_BY]->
            (D IS DOCUMENT)
          COLUMNS (
            D.DOCUMENT_ID AS DOCUMENT_ID,
            D.FILE_NAME AS FILE_NAME,
            D.DOCUMENT_TYPE AS DOCUMENT_TYPE,
            D.VERSION AS DOCUMENT_VERSION,
            D.EFFECTIVE_DATE AS EFFECTIVE_DATE,
            I.INCIDENT_ID AS INCIDENT_ID,
            CAST(NULL AS VARCHAR2(40)) AS EQUIPMENT_ID,
            CAST(NULL AS VARCHAR2(40)) AS MANUFACTURING_LOT,
            CAST(NULL AS NUMBER) AS TASK_ID,
            CAST(NULL AS VARCHAR2(200)) AS TASK_CREATED_BY_AGENT,
            'INCIDENT_REPORT' AS RELATION_TYPE,
            'DOCUMENTED_BY' AS PATH,
            'INCIDENT_CSV' AS SOURCE_TYPE,
            'incidents.csv#' || I.INCIDENT_ID AS SOURCE_REFERENCE_ID,
            CAST(NULL AS VARCHAR2(30)) AS LOT_SOURCE,
            CAST(NULL AS VARCHAR2(200)) AS LOT_SOURCE_REFERENCE_ID
          )
        )
        UNION ALL
        SELECT *
        FROM GRAPH_TABLE (
          LSF_FESTIVAL_OPS_GRAPH
          MATCH
            (I IS INCIDENT)
              -[A IS AFFECTS]->
            (E IS EQUIPMENT)
              -[B IS BELONGS_TO_LOT]->
            (L IS MANUFACTURING_LOT)
              -[G IS GOVERNED_BY]->
            (D IS DOCUMENT)
          COLUMNS (
            D.DOCUMENT_ID AS DOCUMENT_ID,
            D.FILE_NAME AS FILE_NAME,
            D.DOCUMENT_TYPE AS DOCUMENT_TYPE,
            D.VERSION AS DOCUMENT_VERSION,
            D.EFFECTIVE_DATE AS EFFECTIVE_DATE,
            I.INCIDENT_ID AS INCIDENT_ID,
            E.EQUIPMENT_ID AS EQUIPMENT_ID,
            L.MANUFACTURING_LOT AS MANUFACTURING_LOT,
            CAST(NULL AS NUMBER) AS TASK_ID,
            CAST(NULL AS VARCHAR2(200)) AS TASK_CREATED_BY_AGENT,
            G.RELATION_TYPE AS RELATION_TYPE,
            'AFFECTS>BELONGS_TO_LOT>GOVERNED_BY' AS PATH,
            G.SOURCE_TYPE AS SOURCE_TYPE,
            G.SOURCE_REFERENCE_ID AS SOURCE_REFERENCE_ID,
            B.LOT_SOURCE AS LOT_SOURCE,
            B.LOT_SOURCE_REFERENCE_ID AS LOT_SOURCE_REFERENCE_ID
          )
        )
        UNION ALL
        SELECT *
        FROM GRAPH_TABLE (
          LSF_FESTIVAL_OPS_GRAPH
          MATCH
            (I IS INCIDENT)
              -[C IS CREATES]->
            (T IS TASK)
              -[U IS USES_PROCEDURE]->
            (D IS DOCUMENT)
          WHERE T.STATUS IN ('OPEN', 'IN_PROGRESS')
          COLUMNS (
            D.DOCUMENT_ID AS DOCUMENT_ID,
            D.FILE_NAME AS FILE_NAME,
            D.DOCUMENT_TYPE AS DOCUMENT_TYPE,
            D.VERSION AS DOCUMENT_VERSION,
            D.EFFECTIVE_DATE AS EFFECTIVE_DATE,
            I.INCIDENT_ID AS INCIDENT_ID,
            CAST(NULL AS VARCHAR2(40)) AS EQUIPMENT_ID,
            CAST(NULL AS VARCHAR2(40)) AS MANUFACTURING_LOT,
            T.TASK_ID AS TASK_ID,
            T.CREATED_BY_AGENT AS TASK_CREATED_BY_AGENT,
            'TASK_PROCEDURE' AS RELATION_TYPE,
            'CREATES>USES_PROCEDURE' AS PATH,
            U.SOURCE_TYPE AS SOURCE_TYPE,
            U.SOURCE_REFERENCE_ID AS SOURCE_REFERENCE_ID,
            CAST(NULL AS VARCHAR2(30)) AS LOT_SOURCE,
            CAST(NULL AS VARCHAR2(200)) AS LOT_SOURCE_REFERENCE_ID
          )
        )
      ) G
     WHERE G.INCIDENT_ID = P_INCIDENT_ID;

    IF P_RESULT IS NULL THEN
      P_RESULT := TO_CLOB('[]');
    END IF;
  END GET_RELATED_DOCUMENTS;
END LSF_KG_API;
/
