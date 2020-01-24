SELECT * FROM
(SELECT
	DATE(locations.date ) AS "locations.date_date",
	locations.location  AS "locations.location",
	locations.office_id  AS "locations.office_id",
	locations.office_site  AS "locations.office_site",
	locations.area_number  AS "locations.area_number",
	COALESCE(SUM(locations.queries_direct ), 0) AS "locations.queries_direct",
	COALESCE(SUM(locations.queries_indirect ), 0) AS "locations.queries_indirect",
	COALESCE(SUM(locations.views_maps ), 0) AS "locations.views_maps",
	COALESCE(SUM(locations.views_search ), 0) AS "locations.views_search",
	COALESCE(SUM(locations.actions_website ), 0) AS "locations.actions_website",
	COALESCE(SUM(locations.actions_phone ), 0) AS "locations.actions_phone",
	COALESCE(SUM(locations.actions_driving_directions ), 0) AS "locations.actions_driving_directions",
	COALESCE(SUM(locations.local_post_views_search ), 0) AS "locations.local_post_views_search",
	COALESCE(SUM(locations.photos_count_customers ), 0) AS "locations.photos_count_customers",
	COALESCE(SUM(locations.photos_count_merchant ), 0) AS "locations.photos_count_merchant",
	COALESCE(SUM(locations.photos_views_customers ), 0) AS "locations.photos_views_customers",
	COALESCE(SUM(locations.photos_views_merchant ), 0) AS "locations.photos_views_merchant"
FROM google.google_mybusiness_servicebc_derived  AS locations WHERE locations.client = ''servicebc''
GROUP BY 1,2,3,4,5
ORDER BY 1 DESC
LIMIT 50)
