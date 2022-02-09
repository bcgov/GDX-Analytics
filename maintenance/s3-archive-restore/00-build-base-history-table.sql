-- Build a CTE from atomic business area tables
CREATE TABLE test.atomic_sept_30_poc_parquet AS (
    WITH custom_events AS
(
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_workbc_find_career_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_cfmspoc_appointment_step_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_ldb_click_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_form_action_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'    
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_form_error_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_cfmspoc_appointment_step_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_cfmspoc_appointment_click_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_chatbot_chatbot_1 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_chatbot_chatbot_2 WHERE root_tstamp >= '2021-09-30' AND root_tstamp < '2021-10-01'
)
-- Join external table snowplow_web_page_1
SELECT
    wp.id AS page_view_id,
    wp.root_tstamp,
    wp.root_id
FROM custom_events AS ce
JOIN atomic_spectrum_2020_07.snowplow_web_page_1 AS wp
    ON ce.root_id = wp.root_id AND ce.root_tstamp = wp.root_tstamp
WHERE 
    wp.month LIKE '2021-09-01 00:00:00' AND -- Tells Spectrum look only at September partition
    wp.root_tstamp >= '2021-09-30');

GRANT SELECT ON test.atomic_sept_30_poc_parquet to looker;
