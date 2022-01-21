-- Build a CTE from atmoic data and SELECT columns required to build PDTs
-- Where the min root_tstamp is equivalent to two years of data
WITH custom_events AS
(
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_workbc_find_career_1' AS table_name FROM atomic.ca_bc_gov_workbc_find_career_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_cfmspoc_appointment_step_1' AS table_name FROM atomic.ca_bc_gov_cfmspoc_appointment_step_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_ldb_click_1' AS table_name FROM atomic.ca_bc_gov_ldb_click_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_form_action_1' AS table_name FROM atomic.ca_bc_gov_form_action_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'    
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_form_error_1' AS table_name FROM atomic.ca_bc_gov_form_error_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_cfmspoc_appointment_step_1' AS table_name FROM atomic.ca_bc_gov_cfmspoc_appointment_step_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_cfmspoc_appointment_click_1' AS table_name FROM atomic.ca_bc_gov_cfmspoc_appointment_click_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_chatbot_chatbot_1' AS table_name FROM atomic.ca_bc_gov_chatbot_chatbot_1 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
UNION
    SELECT root_id, root_tstamp, 'atomic.ca_bc_gov_chatbot_chatbot_2' AS table_name FROM atomic.ca_bc_gov_chatbot_chatbot_2 WHERE root_tstamp < '2021-11-01' AND root_tstamp >= '2021-10-01'
)

SELECT 
  wp.id AS page_view_id,
  wp.root_tstamp,
  wp.root_id,
  COALESCE(events.page_urlhost,'') AS page_urlhost,
  events.page_url,
  events.domain_sessionid,
  table_name -- debug column for understandability
FROM custom_events AS ce
          JOIN atomic.com_snowplowanalytics_snowplow_web_page_1 AS wp
              ON ce.root_id = wp.root_id AND ce.root_tstamp = wp.root_tstamp
          LEFT JOIN atomic.events ON ce.root_id = events.event_id AND ce.root_tstamp = events.collector_tstamp)