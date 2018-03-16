# If necessary, uncomment the line below to include explore_source.
include: "snowplow_web_block.model.lkml"

view: page_views_rollup {
  derived_table: {
    explore_source: page_views {
      column: session_start_date { field: sessions.session_start_date }
      column: session_count {field: sessions.session_count}
      column: user_count { field: sessions.user_count }
      derived_column: p_key {
        sql: ROW_NUMBER() OVER (ORDER BY TRUE) ;;
      }
    }
  }

  dimension_group: session_start {
    type: time
    timeframes: [raw,date,week]
    sql: ${TABLE}.session_start_date  ;;
  }

  dimension: user_count {
    type: number
  }

  dimension: session_count {
    type: number
  }

  dimension: unique_sessions_1_day_distribution {
    type: tier
    style: integer
    tiers: [0,2,5,10,20,50,75,100,150,500]
    sql: ${session_count} ;;
  }
  dimension: unique_visits_1_day_distribution {
    type: tier
    style: integer
    tiers: [0,20,30,50,75,100,150,300,500,1000]
    sql: ${user_count} ;;
  }

  dimension: p_key {
    primary_key: yes
    hidden: yes
    sql: ${TABLE}.p_key ;;
  }
}
