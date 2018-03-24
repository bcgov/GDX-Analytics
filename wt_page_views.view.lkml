view: wt_page_views {
  label: "Page Views"
  derived_table: {
    sql: SELECT

            -- page

            a.page_urlhost || a.page_urlpath AS page_url,
            a.page_title

            FROM derived.events AS a

            WHERE event_name = 'page_view'
            ;;
  }

  dimension: page_url {
    type: string
    sql: ${TABLE}.page_url ;;
  }

  dimension: page_title {
    type: string
    sql: ${TABLE}.page_title ;;
  }

  measure: page_view_count {
    type: count
    group_label: "Counts"
  }
}
