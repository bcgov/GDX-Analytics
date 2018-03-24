# - dashboard: bcgov_web_analytics
#   title: BCGov Web Analytics
#   layout: newspaper
#   elements:
#   - name: Page Views Section
#     type: text
#     title_text: Page Views
#     row: 9
#     col: 0
#     width: 24
#     height: 2
#   - name: Usage
#     type: text
#     title_text: Usage
#     row: 27
#     col: 0
#     width: 24
#     height: 2
#   - name: Geographic
#     type: text
#     title_text: Geographic
#     body_text: ''
#     row: 45
#     col: 0
#     width: 24
#     height: 2
#   - name: Path Analysis Placeholder
#     type: text
#     title_text: Path Analysis Placeholder
#     row: 53
#     col: 0
#     width: 24
#     height: 2
#   - name: Visits
#     type: text
#     title_text: Visits
#     row: 0
#     col: 0
#     width: 24
#     height: 2
#   - title: Unique Visits
#     name: Unique Visits
#     model: snowplow_web_block
#     explore: page_views
#     type: single_value
#     fields:
#     - sessions.session_start_week
#     - sessions.user_count
#     fill_fields:
#     - sessions.session_start_week
#     filters:
#       sessions.session_start_time: last week, 2 weeks ago
#     sorts:
#     - sessions.session_start_week desc
#     limit: 500
#     column_limit: 50
#     dynamic_fields:
#     - table_calculation: last_week
#       label: Last Week
#       expression: "${sessions.user_count}"
#       value_format:
#       value_format_name:
#       _kind_hint: measure
#       _type_hint: number
#     - table_calculation: 2_weeks_ago
#       label: 2 Weeks Ago
#       expression: "(${last_week}-offset(${sessions.user_count},1))/offset(${sessions.user_count},1)"
#       value_format:
#       value_format_name: percent_0
#       _kind_hint: measure
#       _type_hint: number
#     query_timezone: America/Vancouver
#     custom_color_enabled: false
#     custom_color: forestgreen
#     show_single_value_title: true
#     show_comparison: true
#     comparison_type: change
#     comparison_reverse_colors: false
#     show_comparison_label: true
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     show_null_points: true
#     point_style: circle
#     interpolation: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     trend_lines: []
#     reference_lines: []
#     y_axes:
#     - label: ''
#       maxValue:
#       minValue:
#       orientation: left
#       showLabels: true
#       showValues: true
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: sessions.session_count
#         name: Session Count
#         axisId: sessions.session_count
#     hidden_fields:
#     - sessions.user_count
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#       Page Url: page_views.page_url
#     row: 2
#     col: 0
#     width: 6
#     height: 7
#   - title: Page View Trend
#     name: Page View Trend
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_line
#     fields:
#     - page_views.page_view_count
#     - sessions.session_start_week
#     fill_fields:
#     - sessions.session_start_week
#     sorts:
#     - sessions.session_start_week
#     limit: 500
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: true
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     show_null_points: true
#     point_style: circle
#     interpolation: linear
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     reference_lines:
#     - reference_type: line
#       line_value: mean
#       range_start: max
#       range_end: min
#       margin_top: deviation
#       margin_value: mean
#       margin_bottom: deviation
#       label_position: right
#       color: "#000000"
#       label: ''
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 11
#     col: 6
#     width: 8
#     height: 7
#   - title: Unique Visits Trend
#     name: Unique Visits Trend
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_line
#     fields:
#     - sessions.session_start_week
#     - sessions.user_count
#     fill_fields:
#     - sessions.session_start_week
#     sorts:
#     - sessions.session_start_week desc
#     limit: 500
#     query_timezone: America/Vancouver
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     show_null_points: true
#     point_style: circle
#     interpolation: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     trend_lines: []
#     reference_lines:
#     - reference_type: line
#       line_value: mean
#       range_start: max
#       range_end: min
#       margin_top: deviation
#       margin_value: mean
#       margin_bottom: deviation
#       label_position: right
#       color: "#000000"
#       label: ''
#     y_axes:
#     - label: ''
#       maxValue:
#       minValue:
#       orientation: left
#       showLabels: true
#       showValues: true
#       tickDensity: custom
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: sessions.session_count
#         name: Session Count
#         axisId: sessions.session_count
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 2
#     col: 6
#     width: 8
#     height: 7
#   - title: Page Views per Visit
#     name: Page Views per Visit
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_bar
#     fields:
#     - page_views_rollup.unique_sessions_1_day_distribution
#     - page_views.page_view_count
#     filters:
#       page_views.page_view_count: NOT NULL
#     sorts:
#     - page_views_rollup.unique_sessions_1_day_distribution
#     limit: 500
#     query_timezone: America/Vancouver
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 11
#     col: 14
#     width: 10
#     height: 7
#   - title: Previous Sessions per Users
#     name: Previous Sessions per Users
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_bar
#     fields:
#     - users.user_count
#     - page_views_rollup.unique_sessions_1_day_distribution
#     filters:
#       users.user_count: NOT NULL
#     sorts:
#     - page_views_rollup.unique_visits_1_day_distribution
#     limit: 5000
#     column_limit: 50
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_labels:
#       users.user_count: Count of Users
#     series_types: {}
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 2
#     col: 14
#     width: 10
#     height: 7
#   - title: Page Views
#     name: Page Views
#     model: snowplow_web_block
#     explore: page_views
#     type: single_value
#     fields:
#     - sessions.session_start_week
#     - page_views.page_view_count
#     filters:
#       sessions.session_start_time: last week, 2 weeks ago
#     sorts:
#     - sessions.session_start_week desc
#     limit: 500
#     column_limit: 50
#     dynamic_fields:
#     - table_calculation: last_week
#       label: Last Week
#       expression: "${page_views.page_view_count}"
#       value_format:
#       value_format_name:
#       _kind_hint: measure
#       _type_hint: number
#     - table_calculation: 2_weeks_ago
#       label: 2 Weeks Ago
#       expression: "(${last_week}-offset(${page_views.page_view_count},1))/offset(${page_views.page_view_count},1)"
#       value_format:
#       value_format_name: percent_0
#       _kind_hint: measure
#       _type_hint: number
#     query_timezone: America/Vancouver
#     custom_color_enabled: false
#     custom_color: forestgreen
#     show_single_value_title: true
#     show_comparison: true
#     comparison_type: change
#     comparison_reverse_colors: false
#     show_comparison_label: true
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     show_null_points: true
#     point_style: circle
#     interpolation: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     trend_lines: []
#     reference_lines: []
#     y_axes:
#     - label: ''
#       maxValue:
#       minValue:
#       orientation: left
#       showLabels: true
#       showValues: true
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: sessions.session_count
#         name: Session Count
#         axisId: sessions.session_count
#     hidden_fields:
#     - page_views.page_view_count
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 11
#     col: 0
#     width: 6
#     height: 7
#   - title: Top Pages by Page Views
#     name: Top Pages by Page Views
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_bar
#     fields:
#     - page_views.page_title
#     - page_views.page_view_count
#     - page_views.session_count
#     sorts:
#     - page_views.page_view_count desc
#     limit: 10
#     stacking: ''
#     show_value_labels: true
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     trend_lines: []
#     y_axes:
#     - label: Page Views
#       maxValue:
#       minValue:
#       orientation: top
#       showLabels: true
#       showValues: false
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: page_views.page_view_count
#         name: Page Views
#         axisId: page_views.page_view_count
#     - label: Sessions
#       maxValue:
#       minValue:
#       orientation: bottom
#       showLabels: true
#       showValues: false
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: page_views.session_count
#         name: Visits
#         axisId: page_views.session_count
#     series_types: {}
#     hidden_series: []
#     series_labels:
#       page_views.page_view_count: Page Views
#       page_views.session_count: Sessions
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 18
#     col: 0
#     width: 24
#     height: 9
#   - title: Top Entry Pages
#     name: Top Entry Pages
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_bar
#     fields:
#     - page_views.page_view_count
#     - page_views.first_page_title_test
#     filters:
#       page_views.first_page_title_test: "-EMPTY"
#     sorts:
#     - page_views.page_view_count desc
#     limit: 10
#     stacking: ''
#     show_value_labels: true
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     trend_lines: []
#     y_axes:
#     - label: Page Views
#       maxValue:
#       minValue:
#       orientation: top
#       showLabels: true
#       showValues: false
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: page_views.page_view_count
#         name: Page Views
#         axisId: page_views.page_view_count
#     - label: Sessions
#       maxValue:
#       minValue:
#       orientation: bottom
#       showLabels: true
#       showValues: false
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: page_views.session_count
#         name: Visits
#         axisId: page_views.session_count
#     series_types: {}
#     hidden_series: []
#     series_labels:
#       page_views.page_view_count: Page Views
#       page_views.session_count: Sessions
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 29
#     col: 0
#     width: 12
#     height: 9
#   - title: Top Exit Pages
#     name: Top Exit Pages
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_bar
#     fields:
#     - page_views.last_page_title
#     - page_views.page_view_count
#     filters:
#       page_views.last_page_title: "-EMPTY"
#     sorts:
#     - page_views.page_view_count desc
#     limit: 10
#     column_limit: 50
#     stacking: ''
#     show_value_labels: true
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     show_view_names: false
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     series_types: {}
#     y_axes:
#     - label: ''
#       maxValue:
#       minValue:
#       orientation: top
#       showLabels: true
#       showValues: false
#       tickDensity: default
#       tickDensityCustom: 5
#       type: linear
#       unpinAxis: false
#       valueFormat:
#       series:
#       - id: page_views.page_view_count
#         name: Page View Count
#         axisId: page_views.page_view_count
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 29
#     col: 12
#     width: 12
#     height: 9
#   - title: Search Phrases
#     name: Search Phrases
#     model: snowplow_web_block
#     explore: page_views
#     type: table
#     fields:
#     - page_views.session_count
#     - page_views.search_field
#     filters:
#       page_views.search_field: "-EMPTY"
#     sorts:
#     - page_views.session_count desc
#     limit: 10
#     dynamic_fields:
#     - table_calculation: percent_of_total
#       label: Percent of Total
#       expression: "${page_views.session_count}/sum(${page_views.session_count})"
#       value_format:
#       value_format_name: percent_1
#       _kind_hint: measure
#       _type_hint: number
#     query_timezone: America/Vancouver
#     show_view_names: true
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     limit_displayed_rows: false
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     hidden_fields:
#     - percent_of_total
#     series_types: {}
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 38
#     col: 0
#     width: 8
#     height: 7
#   - title: Top Referral Source
#     name: Top Referral Source
#     model: snowplow_web_block
#     explore: page_views
#     type: table
#     fields:
#     - page_views.session_count
#     - page_views.referer_url_host
#     filters:
#       page_views.referer_url_host: "-EMPTY"
#     sorts:
#     - page_views.session_count desc
#     limit: 10
#     show_view_names: false
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     limit_displayed_rows: false
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 38
#     col: 8
#     width: 8
#     height: 7
#   - title: Top Traffic Source
#     name: Top Traffic Source
#     model: snowplow_web_block
#     explore: page_views
#     type: table
#     fields:
#     - page_views.referer_medium
#     - page_views.session_count
#     limit: 500
#     show_view_names: true
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     limit_displayed_rows: false
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     series_types: {}
#     row: 38
#     col: 16
#     width: 8
#     height: 7
#   - title: B.C. User Locations
#     name: Local User Locations
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_map
#     fields:
#     - page_views.geo_city
#     - users.user_count
#     - page_views.geo_location
#     - page_views.page_view_count
#     filters:
#       page_views.geo_country: CA
#       page_views.geo_region: BC
#     sorts:
#     - users.user_count desc
#     limit: 500
#     column_limit: 50
#     map_plot_mode: points
#     heatmap_gridlines: false
#     heatmap_gridlines_empty: false
#     heatmap_opacity: 0.5
#     show_region_field: true
#     draw_map_labels_above_data: true
#     map_tile_provider: positron
#     map_position: custom
#     map_scale_indicator: 'off'
#     map_pannable: true
#     map_zoomable: true
#     map_marker_type: circle
#     map_marker_icon_name: default
#     map_marker_radius_mode: proportional_value
#     map_marker_units: pixels
#     map_marker_proportional_scale_type: linear
#     map_marker_color_mode: value
#     show_view_names: true
#     show_legend: true
#     quantize_map_value_colors: false
#     reverse_map_value_colors: false
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     show_null_points: true
#     point_style: none
#     interpolation: linear
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     custom_color_enabled: false
#     custom_color: forestgreen
#     show_single_value_title: true
#     show_comparison: false
#     comparison_type: value
#     comparison_reverse_colors: false
#     show_comparison_label: true
#     ordering: none
#     show_null_labels: false
#     series_types: {}
#     hidden_series: []
#     map_latitude: 49.76784066763264
#     map_longitude: -121.67960286140443
#     map_zoom: 5
#     map_marker_radius_min:
#     map_marker_radius_max: 20
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 47
#     col: 0
#     width: 12
#     height: 6
#   - title: International User Locations
#     name: International User Locations
#     model: snowplow_web_block
#     explore: page_views
#     type: looker_map
#     fields:
#     - page_views.geo_city
#     - users.user_count
#     - page_views.geo_location
#     - page_views.page_view_count
#     filters:
#       page_views.geo_country: "-CA"
#     sorts:
#     - users.user_count desc
#     limit: 500
#     column_limit: 50
#     map_plot_mode: points
#     heatmap_gridlines: false
#     heatmap_gridlines_empty: false
#     heatmap_opacity: 0.5
#     show_region_field: true
#     draw_map_labels_above_data: true
#     map_tile_provider: positron
#     map_position: custom
#     map_scale_indicator: 'off'
#     map_pannable: true
#     map_zoomable: true
#     map_marker_type: circle
#     map_marker_icon_name: default
#     map_marker_radius_mode: proportional_value
#     map_marker_units: pixels
#     map_marker_proportional_scale_type: linear
#     map_marker_color_mode: value
#     show_view_names: true
#     show_legend: true
#     quantize_map_value_colors: false
#     reverse_map_value_colors: false
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     limit_displayed_rows: false
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     show_null_points: true
#     point_style: none
#     interpolation: linear
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     custom_color_enabled: false
#     custom_color: forestgreen
#     show_single_value_title: true
#     show_comparison: false
#     comparison_type: value
#     comparison_reverse_colors: false
#     show_comparison_label: true
#     ordering: none
#     show_null_labels: false
#     series_types: {}
#     hidden_series: []
#     map_latitude: 24.835397956211832
#     map_longitude: 354.8408138751984
#     map_zoom: 2
#     map_marker_radius_max: 8
#     listen:
#       Session Date: sessions.session_start_date
#       Is Government User: page_views.is_government
#       Country: page_views.geo_country
#       Region: page_views.geo_region_name
#       City: page_views.geo_city
#       Device Mobile?: page_views.device_is_mobile
#     row: 47
#     col: 12
#     width: 12
#     height: 6
#   - name: Action Center
#     type: text
#     title_text: Action Center
#     row: 55
#     col: 0
#     width: 24
#     height: 2
#   - title: Top Single Page Visits
#     name: Top Single Page Visits
#     model: snowplow_web_block
#     explore: page_views
#     type: table
#     fields:
#     - page_views.page_url
#     - page_views.average_page_views_per_visit
#     - page_views.page_view_count
#     - page_views.average_time_engaged
#     filters:
#       page_views.average_page_views_per_visit: '1'
#     sorts:
#     - page_views.page_view_count desc
#     limit: 10
#     column_limit: 50
#     show_view_names: true
#     show_row_numbers: true
#     truncate_column_names: false
#     hide_totals: false
#     hide_row_totals: false
#     table_theme: editable
#     limit_displayed_rows: false
#     enable_conditional_formatting: false
#     conditional_formatting_include_totals: false
#     conditional_formatting_include_nulls: false
#     stacking: ''
#     show_value_labels: false
#     label_density: 25
#     legend_position: center
#     x_axis_gridlines: false
#     y_axis_gridlines: true
#     y_axis_combined: true
#     show_y_axis_labels: true
#     show_y_axis_ticks: true
#     y_axis_tick_density: default
#     y_axis_tick_density_custom: 5
#     show_x_axis_label: true
#     show_x_axis_ticks: true
#     x_axis_scale: auto
#     y_axis_scale_mode: linear
#     ordering: none
#     show_null_labels: false
#     show_totals_labels: false
#     show_silhouette: false
#     totals_color: "#808080"
#     custom_color_enabled: false
#     custom_color: forestgreen
#     show_single_value_title: true
#     show_comparison: false
#     comparison_type: value
#     comparison_reverse_colors: false
#     show_comparison_label: true
#     map_plot_mode: points
#     heatmap_gridlines: false
#     heatmap_gridlines_empty: false
#     heatmap_opacity: 0.5
#     show_region_field: true
#     draw_map_labels_above_data: true
#     map_tile_provider: positron
#     map_position: fit_data
#     map_scale_indicator: 'off'
#     map_pannable: true
#     map_zoomable: true
#     map_marker_type: circle
#     map_marker_icon_name: default
#     map_marker_radius_mode: proportional_value
#     map_marker_units: meters
#     map_marker_proportional_scale_type: linear
#     map_marker_color_mode: fixed
#     show_legend: true
#     quantize_map_value_colors: false
#     reverse_map_value_colors: false
#     value_labels: legend
#     label_type: labPer
#     show_null_points: true
#     point_style: circle
#     interpolation: linear
#     hidden_fields:
#     - page_views.average_page_views_per_visit
#     series_types: {}
#     row: 57
#     col: 0
#     width: 24
#     height: 6
#   - name: Top 404 Pages Placeholder
#     type: text
#     title_text: Top 404 Pages Placeholder
#     row: 63
#     col: 0
#     width: 24
#     height: 2
#   - name: Offsite Links Placeholder
#     type: text
#     title_text: Offsite Links Placeholder
#     row: 65
#     col: 0
#     width: 24
#     height: 2
#   # filters:
#   # - name: Session Date
#   #   title: Session Date
#   #   type: field_filter
#   #   default_value: NOT NULL
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: sessions.session_start_date
#   #   listens_to_filters: []
#   #   allow_multiple_values: true
#   #   required: false
#   # - name: Is Government User
#   #   title: Is Government User
#   #   type: field_filter
#   #   default_value: 'No'
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: page_views.is_government
#   #   listens_to_filters: []
#   #   allow_multiple_values: true
#   #   required: false
#   # - name: Country
#   #   title: Country
#   #   type: field_filter
#   #   default_value: ''
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: page_views.geo_country
#   #   listens_to_filters: []
#   #   allow_multiple_values: true
#   #   required: false
#   # - name: Region
#   #   title: Region
#   #   type: field_filter
#   #   default_value: ''
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: page_views.geo_region_name
#   #   listens_to_filters:
#   #   - Country
#   #   allow_multiple_values: true
#   #   required: false
#   # - name: City
#   #   title: City
#   #   type: field_filter
#   #   default_value: ''
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: page_views.geo_city
#   #   listens_to_filters:
#   #   - Country
#   #   allow_multiple_values: true
#   #   required: false
#   # - name: Device Mobile?
#   #   title: Device Mobile?
#   #   type: field_filter
#   #   default_value: 'No'
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: page_views.device_is_mobile
#   #   listens_to_filters: []
#   #   allow_multiple_values: true
#   #   required: false
#   # - name: Page Url
#   #   title: Page Url
#   #   type: field_filter
#   #   default_value: ''
#   #   model: snowplow_web_block
#   #   explore: page_views
#   #   field: page_views.page_url
#   #   listens_to_filters: []
#   #   allow_multiple_values: true
#   #   required: false
