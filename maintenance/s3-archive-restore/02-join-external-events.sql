-- Update on cluster history table with
-- archived external atomic events data
UPDATE gdx_analytics.restored_atomic_ca_bc_gov
    SET page_urlhost = ev.page_urlhost,
        page_url = ev.page_url,
        domain_sessionid = ev.domain_sessionid
FROM atomic_spectrum_2020_07.events AS ev
    WHERE
        -- spectrum partition filter month and app_id
        ev.month = '2021-09-01 00:00:00' AND
        atomic_sept_poc_parquet.root_id = ev.event_id AND
        atomic_sept_poc_parquet.root_tstamp = ev.collector_tstamp;
