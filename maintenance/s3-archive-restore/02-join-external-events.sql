-- Build CTE with external atomic events data
WITH he AS (
    SELECT
        ev.event_id,
        ev.collector_tstamp,
        ev.page_urlhost,
        ev.page_url,
        ev.domain_sessionid
    FROM atomic_spectrum_2020_07.events AS ev
        INNER JOIN test.atomic_sept_full_poc_parquet AS ta
            ON ta.root_id = ev.event_id AND
            ta.root_tstamp = ev.collector_tstamp
        WHERE
            -- wp.month limits spectrum s3 scan to specified partition 
            ev.month LIKE '2021-09-01 00:00:00' AND
            ta.root_tstamp >= '2021-09-01'
)
-- update the base table with historical events data
UPDATE test.atomic_sept_full_poc_parquet
    SET page_urlhost = he.page_urlhost,
        page_url = he.page_url,
        domain_sessionid = he.domain_sessionid
FROM he
    WHERE atomic_sept_full_poc_parquet.root_id = he.event_id AND
    atomic_sept_full_poc_parquet.root_tstamp = he.collector_tstamp;
