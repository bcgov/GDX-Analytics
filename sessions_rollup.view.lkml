# If necessary, uncomment the line below to include explore_source.
include: "snowplow_web_block.model.lkml"

view: sessions_rollup {
  derived_table: {
    explore_source: page_views {
      column: session_id {}
      column: max_page_view_index {}
    }
  }
  dimension: session_id {
    primary_key: yes
  }
  dimension: max_page_view_index {
    type: number
  }
}
