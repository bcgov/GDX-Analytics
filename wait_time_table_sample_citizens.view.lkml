view: wait_time_table_sample_citizens {
  derived_table: {
    sql: WITH step1 AS(
      SELECT
        event_name,
        derived_tstamp AS event_time,
        DATEDIFF(seconds, LAG(derived_tstamp) OVER (PARTITION BY ticket_number ORDER BY event_time), derived_tstamp) AS wait_time,
        ticket_number,
        postal_code,
        location AS office_location,
        id AS agent_id,
        source AS arrival_source,
        service,
        details AS information,
        destination AS referral_destination,
        success AS resolution
      FROM atomic.events AS ev
      LEFT JOIN atomic.ca_bc_gov_poc_citizen_1 AS c
      ON ev.event_id = c.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_office_1 AS o
      ON ev.event_id = o.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_agent_1 AS a
      ON ev.event_id = a.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_arrival_1 AS ar
      ON ev.event_id = ar.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_application_1 AS ap
      ON ev.event_id = ap.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_information_1 AS i
      ON ev.event_id = i.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_referral_1 AS rf
      ON ev.event_id = rf.root_id
      LEFT JOIN atomic.ca_bc_gov_poc_resolution_1 AS rp
      ON ev.event_id = rp.root_id
      WHERE app_id = 'demo'
      )

      SELECT
        event_name,
        event_time,
        wait_time,
        SUM(CASE WHEN event_name in ('application', 'information', 'referral', 'resolution') THEN wait_time END) OVER (PARTITION BY ticket_number) AS total_wait_time,
        SUM(CASE WHEN event_name in ('information', 'referral', 'resolution') THEN wait_time END) OVER (PARTITION BY ticket_number) AS resolution_time,
        ticket_number,
        postal_code,
        office_location,
        agent_id,
        arrival_source,
        service,
        information,
        referral_destination,
        resolution
      FROM step1
      ORDER BY 2
       ;;
  }

  measure: count {
    type: count
    drill_fields: [detail*]
  }

  measure: average_total_wait_time {
    type:  average
    sql: ${total_wait_time} ;;
    value_format: "0.00\"s\""
  }

  measure: average_wait_time {
    type:  average
    sql: ${wait_time} ;;
    value_format: "0.00\"s\""
  }

  measure: average_resolution_time {
    type:  average
    sql: ${resolution_time} ;;
    value_format: "0.00\"s\""
  }

  dimension: event_name {
    type: string
    sql: ${TABLE}.event_name ;;
  }

  dimension: event_time {
    type: string
    sql: ${TABLE}.event_time ;;
  }

  dimension: wait_time {
    type: number
    sql: ${TABLE}.wait_time ;;
    value_format: "0\"s\""
  }

  dimension: total_wait_time {
    type: number
    sql: ${TABLE}.total_wait_time ;;
    value_format: "0\"s\""
  }

  dimension: resolution_time {
    type: number
    sql: ${TABLE}.resolution_time ;;
    value_format: "0\"s\""
  }

  dimension: ticket_number {
    type: string
    sql: ${TABLE}.ticket_number ;;
  }

  dimension: postal_code {
    type: string
    sql: ${TABLE}.postal_code ;;
  }

  dimension: office_location {
    type: string
    sql: ${TABLE}.office_location ;;
  }

  dimension: agent_id {
    type: string
    sql: ${TABLE}.agent_id ;;
  }

  dimension: arrival_source {
    type: string
    sql: ${TABLE}.arrival_source ;;
  }

  dimension: service {
    type: string
    sql: ${TABLE}.service ;;
  }

  dimension: information {
    type: string
    sql: ${TABLE}.information ;;
  }

  dimension: referral_destination {
    type: string
    sql: ${TABLE}.referral_destination ;;
  }

  dimension: resolution {
    type: string
    sql: ${TABLE}.resolution ;;
  }

  set: detail {
    fields: [
      event_name,
      event_time,
      wait_time,
      total_wait_time,
      resolution_time,
      ticket_number,
      postal_code,
      office_location,
      agent_id,
      arrival_source,
      service,
      information,
      referral_destination,
      resolution
    ]
  }
}
