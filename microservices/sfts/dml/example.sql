SELECT * FROM servicebc.cats_gdx where gdx_id IN
(SELECT gdx_id FROM servicebc.cats_gdx ORDER BY gdx_id DESC LIMIT 1)
