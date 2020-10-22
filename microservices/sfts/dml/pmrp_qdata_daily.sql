SELECT * FROM(
    SELECT
	cfms_poc.agent_id  AS "cfms_poc.agent_id",
	cfms_poc.back_office  AS "cfms_poc.back_office",
	cfms_poc.channel_sort  AS "cfms_poc.channel_sort",
	cfms_poc.channel  AS "cfms_poc.channel",
	cfms_poc.client_id  AS "cfms_poc.client_id",
	cfms_poc.counter_type  AS "cfms_poc.counter_type",
	DATE(cfms_poc.welcome_time ) AS "cfms_poc.date",
	CASE WHEN cfms_poc.inaccurate_time  THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.inaccurate_time",
        CASE WHEN cfms_poc.no_wait_visit  THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.no_wait_visit",
        cfms_poc.office_id  AS "cfms_poc.office_id",
        cfms_poc.office_name  AS "cfms_poc.office_name",
        cfms_poc.program_id  AS "cfms_poc.program_id",
        cfms_poc.service_count  AS "cfms_poc.service_count",
        COALESCE(cfms_poc.status, 'Open Ticket') AS "cfms_poc.status",
        TO_CHAR(DATE_TRUNC('second', cfms_poc.welcome_time ), 'YYYY-MM-DD HH24:MI:SS') AS "cfms_poc.welcome_time",
        TO_CHAR(DATE_TRUNC('second', cfms_poc.latest_time ), 'YYYY-MM-DD HH24:MI:SS') AS "cfms_poc.latest_time",
        CASE WHEN abs(cfms_poc.service_creation_duration_zscore) >= 3  THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.service_creation_duration_outlier",
        CASE WHEN abs(cfms_poc.waiting_duration_zscore) >= 3  THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.waiting_duration_outlier",
        CASE WHEN abs(cfms_poc.prep_duration_zscore) >= 3  THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.prep_duration_outlier",
        CASE WHEN abs( cfms_poc.serve_duration_zscore) >= 3 THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.serve_duration_outlier",
        CASE WHEN abs(cfms_poc.hold_duration_zscore) >= 3  THEN 'Yes' ELSE 'No' END
    AS "cfms_poc.hold_duration_outlier",
        (1.00 * cfms_poc.serve_duration)/(60*60*24)  AS "cfms_poc.serve_duration_per_service",
        (1.00 * cfms_poc.serve_duration_total)/(60*60*24)  AS "cfms_poc.serve_duration_per_visit",
        (1.00 * cfms_poc.prep_duration)/(60*60*24)  AS "cfms_poc.prep_duration_per_service",
        (1.00 * cfms_poc.prep_duration_total)/(60*60*24)  AS "cfms_poc.prep_duration_per_visit",
        (1.00 * cfms_poc.waiting_duration)/(60*60*24)  AS "cfms_poc.waiting_duration_per_service",
        (1.00 * cfms_poc.waiting_duration_total)/(60*60*24)  AS "cfms_poc.waiting_duration_per_visit",
        (1.00 * cfms_poc.hold_duration)/(60*60*24)  AS "cfms_poc.hold_duration_per_service",
        (1.00 * cfms_poc.hold_duration_total)/(60*60*24)  AS "cfms_poc.hold_duration_per_visit",
        COUNT (DISTINCT cfms_poc.client_id )  AS "cfms_poc.visits_count",
        COUNT(*) AS "cfms_poc.services_count",
        COALESCE(SUM(cfms_poc.transaction_count ), 0) AS "cfms_poc.transactions_count"
    FROM derived.theq_step1  AS cfms_poc

    WHERE ((((cfms_poc.welcome_time ) >= ((DATEADD(day,-1, DATE_TRUNC('day',GETDATE()) ))) AND (cfms_poc.welcome_time ) < ((DATEADD(day,1, DATEADD(day,-1, DATE_TRUNC('day',GETDATE()) ) )))))) AND (((TRANSLATE(TRANSLATE(cfms_poc.office_name, ' ', '_'),'.','')) LIKE '%'))
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29
    ORDER BY 7 DESC
)
