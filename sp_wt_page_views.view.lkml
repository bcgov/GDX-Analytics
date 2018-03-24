view: sp_wt_page_views {
  derived_table: {
    sql:
        SELECT
          page_title, page_url
        FROM atomic.events AS sp_page_views
        WHERE sp_page_views.event = 'page_view'

        UNION ALL

        SELECT
          page_title, page_url
        FROM derived.events AS wt_page_views
        WHERE wt_page_views.event = 'page_view'

             ;;
    # Do not persist for now!!! don't want this overriding other scratch tables.
    #sql_trigger_value: SELECT COUNT(*) FROM ${scratch_pv_05.SQL_TABLE_NAME} ;;
    #distribution: "user_snowplow_domain_id"
    #sortkeys: ["page_view_start"]
  }

  # DIMENSIONS

  # Page

  dimension: page_url {
    type: string
    sql: ${TABLE}.page_url ;;
    group_label: "Page"
  }

  dimension: page_title {
    type: string
    sql: ${TABLE}.page_title ;;
    group_label: "Page"
  }

  # MEASURES

  measure: row_count {
    type: count
    group_label: "Counts"
  }

}
