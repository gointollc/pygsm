-- This file should be used to create the initial DB schema and to 
-- populate any necessary static data during installation of pygsm
-- 
-- requires Postgresql 9.6+
-- 

CREATE TABLE game (
    game_uuid uuid UNIQUE PRIMARY KEY,
    game_id varchar,
    stamp timestamp default now()
);
CREATE INDEX game__stamp__idx ON game (stamp);

CREATE TABLE ping (
    ping_id serial PRIMARY KEY,
    hostname varchar, 
    port int, 
    name varchar,
    ping timestamp,
    active int,
    max int,
    dev boolean,
    game_uuid uuid REFERENCES game (game_uuid),
    UNIQUE (hostname, port)
);
CREATE INDEX ping__ping__idx ON ping (ping);
CREATE INDEX ping__dev ON ping (dev);

CREATE TABLE game_player (
    game_player_id serial PRIMARY KEY,
    game_uuid uuid REFERENCES game (game_uuid),
    meta jsonb,
    UNIQUE (game_player_id, game_uuid)
);
CREATE INDEX game_player__game_uuid__idx ON game_player (game_uuid);

CREATE TABLE leaderboard (
    leaderboard_id serial PRIMARY KEY,
    game_player_id int REFERENCES game_player (game_player_id),
    kills int,
    deaths int
);
CREATE INDEX leaderboard__game_player_id__idx ON leaderboard (game_player_id);