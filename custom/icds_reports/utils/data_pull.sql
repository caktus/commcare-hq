SELECT
    awc.state_name,
    awc.district_name,
    awc.block_name,
    awc.supervisor_name,
    awc.awc_name,
    ccs.person_name,
    ccs.ccs_status,
    ccs.age_in_months
    FROM "ccs_record_monthly" ccs
    INNER JOIN "awc_location" awc ON (
        awc.doc_id = ccs.awc_id
        AND awc.supervisor_id = ccs.supervisor_id
        AND awc.aggregation_level = 5
    )
    WHERE
    ccs.age_in_months >= 132 AND ccs.age_in_months<168
    AND (ccs.pregnant=1 OR ccs.lactating=1)
    AND ccs.month = '2020-02-01'
    AND awc.state_is_test IS DISTINCT FROM 1
    AND awc_is_test IS DISTINCT FROM 1;
    
--                                                                                 QUERY PLAN
-- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--  Custom Scan (Citus Real-Time)  (cost=0.00..0.00 rows=0 width=0)
--    Task Count: 64
--    Tasks Shown: One of 64
--    ->  Task
--          Node: host=100.71.184.232 port=6432 dbname=icds_ucr
--          ->  Nested Loop  (cost=1.10..160571.31 rows=1 width=116)
--                ->  Index Scan using crm_supervisor_person_month_idx_102712 on ccs_record_monthly_102712 ccs  (cost=0.56..160537.86 rows=12 width=105)
--                      Index Cond: (month = '2020-02-01'::date)
--                      Filter: ((age_in_months >= 132) AND (age_in_months < 168) AND ((pregnant = 1) OR (lactating = 1)))
--                ->  Index Scan using awc_location_indx6_102840 on awc_location_102840 awc  (cost=0.55..2.78 rows=1 width=140)
--                      Index Cond: (doc_id = ccs.awc_id)
--                      Filter: ((state_is_test IS DISTINCT FROM 1) AND (awc_is_test IS DISTINCT FROM 1) AND (aggregation_level = 5) AND (ccs.supervisor_id = supervisor_id))
-- (12 rows)
