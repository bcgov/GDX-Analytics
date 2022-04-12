-- Build CTE from atomic business area tables
INSERT INTO gdx_analytics.restored_atomic_ca_bc_gov

WITH custom_context_events AS
(
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_workbc_find_career_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.bc_gov_workbc_resource_click_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.bc_gov_workbc_find_resources_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.bc_gov_wellbeing_wellbeing_click_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_wellbeing_wellbeing_resources_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_wellbeing_wellbeing_wordcloud_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_bcs_calendar_click_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_googtrans_google_translate_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_gateway_action_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_ldb_click_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_form_action_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'    
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_form_error_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_cfmspoc_appointment_step_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_cfmspoc_appointment_click_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_chatbot_chatbot_1 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
UNION
    SELECT root_id, root_tstamp FROM atomic.ca_bc_gov_chatbot_chatbot_2 WHERE root_tstamp >= '2021-09-01' AND root_tstamp < '2021-10-01'
)

SELECT
    wp.root_tstamp,
    wp.id AS page_view_id,
    wp.root_id
FROM custom_context_events AS ce
-- join external_schema.glue_data_catalog_table
JOIN atomic_spectrum_2020_07.snowplow_web_page_1 AS wp
    ON ce.root_id = wp.root_id AND ce.root_tstamp = wp.root_tstamp
WHERE
    -- wp.month limits spectrum s3 scan to specified partition 
    wp.month LIKE '2021-09-01 00:00:00' AND
    -- anecdotal performance gain from timestamp condition
    wp.root_tstamp >= '2021-09-01'
GROUP BY 
    wp.root_tstamp,
    wp.id,
    wp.root_id;

GRANT SELECT ON gdx_analytics.restored_atomic_ca_bc_gov TO looker;
