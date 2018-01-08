view: aggregated_table_sample_citizens {
  derived_table: {
    sql: WITH step1 AS (
      SELECT
        c.ticket_number,
        c.postal_code,
        ev.derived_tstamp AS arrival_timestamp,
        ar.source AS arrival_source
      FROM
        atomic.events AS ev
        INNER JOIN atomic.ca_bc_gov_poc_citizen_1 AS c
        ON ev.event_id = c.root_id
        INNER JOIN atomic.ca_bc_gov_poc_arrival_1 AS ar
        ON ev.event_id = ar.root_id
      WHERE ev.event_name = 'arrival'
      GROUP BY 1, 2, 3, 4
      ORDER BY 1
      ),
        step2 AS(
      SELECT
        c.ticket_number,
        ev.derived_tstamp AS application_timestamp,
        ap.service AS application_service,
        a.id AS agent_id,
        a.name AS agent_name,
        a.role AS agent_role,
        o.location AS office_location,
        o.name AS office_name
      FROM
        atomic.events AS ev
        INNER JOIN atomic.ca_bc_gov_poc_citizen_1 AS c
        ON ev.event_id = c.root_id
        INNER JOIN atomic.ca_bc_gov_poc_application_1 AS ap
        ON ev.event_id = ap.root_id
        INNER JOIN atomic.ca_bc_gov_poc_agent_1 AS a
        ON ev.event_id = a.root_id
        INNER JOIN atomic.ca_bc_gov_poc_office_1 AS o
        ON ev.event_id = o.root_id
      WHERE ev.event_name = 'application'
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
      ORDER BY 1
      ),
      step3 AS(
      SELECT
        c.ticket_number,
        ev.derived_tstamp AS information_timestamp,
        i.details AS information_details
      FROM
        atomic.events AS ev
        INNER JOIN atomic.ca_bc_gov_poc_citizen_1 AS c
        ON ev.event_id = c.root_id
        INNER JOIN atomic.ca_bc_gov_poc_information_1 AS i
        ON ev.event_id = i.root_id
      WHERE ev.event_name = 'information'
      GROUP BY 1, 2, 3
      ORDER BY 1
      ),
      step4 AS(
      SELECT
        c.ticket_number,
        ev.derived_tstamp AS referral_timestamp,
        rf.destination AS referral_destination
      FROM
        atomic.events AS ev
        INNER JOIN atomic.ca_bc_gov_poc_citizen_1 AS c
        ON ev.event_id = c.root_id
        INNER JOIN atomic.ca_bc_gov_poc_referral_1 AS rf
        ON ev.event_id = rf.root_id
      WHERE ev.event_name = 'referral'
      GROUP BY 1, 2, 3
      ORDER BY 1
      ),
      step5 AS(
      SELECT
        c.ticket_number,
        ev.derived_tstamp AS resolution_timestamp,
        rs.success AS resolution_success
      FROM
        atomic.events AS ev
        INNER JOIN atomic.ca_bc_gov_poc_citizen_1 AS c
        ON ev.event_id = c.root_id
        INNER JOIN atomic.ca_bc_gov_poc_resolution_1 AS rs
        ON ev.event_id = rs.root_id
      WHERE ev.event_name = 'resolution'
      GROUP BY 1, 2, 3
      ORDER BY 1
      )
      SELECT
        s1.ticket_number,
        s1.postal_code,
        s1.arrival_timestamp,
        s1.arrival_source,
        s2.application_timestamp,
        s2.application_service,
        s2.agent_id,
        s2.agent_name,
        s2.agent_role,
        s2.office_location,
        s2.office_name,
        s3.information_timestamp,
        s3.information_details,
        s4.referral_timestamp,
        s4.referral_destination,
        s5.resolution_timestamp,
        s5.resolution_success
      FROM
        step1 AS s1
        INNER JOIN step2 AS s2
        ON s1.ticket_number = s2.ticket_number
        INNER JOIN step3 as s3
        ON s1.ticket_number = s3.ticket_number
        INNER JOIN step4 as s4
        ON s1.ticket_number = s4.ticket_number
        INNER JOIN step5 as s5
        ON s1.ticket_number = s5.ticket_number
      GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
      ORDER BY 1 ASC
       ;;
  }

  measure: count {
    type: count
    drill_fields: [detail*]
  }

  dimension: ticket_number {
    type: string
    sql: ${TABLE}.ticket_number ;;
  }

  dimension: postal_code {
    type: string
    sql: ${TABLE}.postal_code ;;
  }

  dimension: arrival_timestamp {
    type: string
    sql: ${TABLE}.arrival_timestamp ;;
  }

  dimension: arrival_source {
    type: string
    sql: ${TABLE}.arrival_source ;;
  }

  dimension: application_timestamp {
    type: string
    sql: ${TABLE}.application_timestamp ;;
  }

  dimension: application_service {
    type: string
    sql: ${TABLE}.application_service ;;
  }

  dimension: agent_id {
    type: string
    sql: ${TABLE}.agent_id ;;
  }

  dimension: agent_name {
    type: string
    sql: ${TABLE}.agent_name ;;
  }

  dimension: agent_role {
    type: string
    sql: ${TABLE}.agent_role ;;
  }

  dimension: office_location {
    type: string
    sql: ${TABLE}.office_location ;;
  }

  dimension: office_name {
    type: string
    sql: ${TABLE}.office_name ;;
  }

  dimension: information_timestamp {
    type: string
    sql: ${TABLE}.information_timestamp ;;
  }

  dimension: information_details {
    type: string
    sql: ${TABLE}.information_details ;;
  }

  dimension: referral_timestamp {
    type: string
    sql: ${TABLE}.referral_timestamp ;;
  }

  dimension: referral_destination {
    type: string
    sql: ${TABLE}.referral_destination ;;
  }

  dimension: resolution_timestamp {
    type: string
    sql: ${TABLE}.resolution_timestamp ;;
  }

  dimension: resolution_success {
    type: string
    sql: ${TABLE}.resolution_success ;;
  }

  set: detail {
    fields: [
      ticket_number,
      postal_code,
      arrival_timestamp,
      arrival_source,
      application_timestamp,
      application_service,
      agent_id,
      agent_name,
      agent_role,
      office_location,
      office_name,
      information_timestamp,
      information_details,
      referral_timestamp,
      referral_destination,
      resolution_timestamp,
      resolution_success
    ]
  }
}
