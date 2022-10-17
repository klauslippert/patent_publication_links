\echo PSQL: create patent.stage
---
create table if not exists patente.stage (
    loaddate timestamp NOT NULL DEFAULT now(),
    "data" xml NULL,
    hash text NOT NULL
);
CREATE OR REPLACE FUNCTION hash_update() RETURNS trigger AS $$
BEGIN
    IF tg_op = 'INSERT' OR tg_op = 'UPDATE' THEN
        NEW.hash = encode(digest(new."data"::text, 'sha1'), 'hex');
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER "trigger_hash_update"
                 BEFORE INSERT OR UPDATE of "data" ON patente.stage
                 FOR EACH ROW EXECUTE PROCEDURE hash_update()
;
