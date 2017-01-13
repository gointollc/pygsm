-- This file should be used to create the initial DB schema and to 
-- populate any necessary static data during installation of pygsm
-- 
-- requires Postgresql 9.6+
-- 

CREATE EXTENSION "uuid-ossp";

CREATE TABLE game (
    game_uuid uuid UNIQUE PRIMARY KEY DEFAULT uuid_generate_v4(),
    stamp timestamp DEFAULT NOW() NOT NULL,
    dev boolean DEFAULT TRUE
);
CREATE INDEX game__stamp__idx ON game (stamp);

CREATE TABLE ping (
    ping_id serial PRIMARY KEY,
    hostname varchar NOT NULL, 
    port int NOT NULL, 
    name varchar NOT NULL,
    active int NOT NULL,
    max int NOT NULL,
    dev boolean DEFAULT TRUE,
    down boolean DEFAULT FALSE,
    ping timestamp DEFAULT NOW() NOT NULL,
    game_uuid uuid REFERENCES game (game_uuid) NOT NULL,
    UNIQUE (hostname, port)
);
CREATE INDEX ping__ping__idx ON ping (ping);
CREATE INDEX ping__dev ON ping (dev);

CREATE TABLE game_player (
    game_player_id serial PRIMARY KEY,
    game_uuid uuid REFERENCES game (game_uuid) NOT NULL,
    meta jsonb,
    UNIQUE (game_player_id, game_uuid)
);
CREATE INDEX game_player__game_uuid__idx ON game_player (game_uuid);

CREATE TABLE leaderboard (
    leaderboard_id serial PRIMARY KEY,
    game_player_id int REFERENCES game_player (game_player_id) NOT NULL,
    kills int NOT NULL,
    deaths int NOT NULL
);
CREATE INDEX leaderboard__game_player_id__idx ON leaderboard (game_player_id);

CREATE TABLE psk (
    psk varchar PRIMARY KEY,
    development boolean DEFAULT TRUE,
    description text,
    active boolean DEFAULT TRUE
);