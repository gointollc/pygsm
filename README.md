# Python Game Server Manager (pygsm)

To store and provide information about running game servers

## Setup

### Setup DB Schema

To setup the base DB schema use the file `sql/0000_initial.sql`.

```
psql -1f sql/0000_initial.sql -h [hostname] [database_name]
````

### Install Dependencies 

`pip install -r requirements.txt`

### Configure

Copy `pygsm.cfg.tpl` to `pygsm.cfg`.  

```
cp pygsm.cfg.tpl pygsm.cfg
```

Then edit `pygsm.cfg` with the proper configuration for your instance.  The `Database` and `Logging` sections are required.

## Run

You can run it simply by using the command `hug -f pygsm.py`.  This is not exactly appropriate for production use, so see the following section for setup with WSGI.

### WSGI 

TODO

## Use

### Headers

`X-Api-Key`
:  This header is required for any API call that writes to the database.  It needs to be a PSK that is active in the database.  It also differentiates between development and production data.

### GET,POST /auth-test

**Authentication**: Required

A simple method to test out authentication.

### GET /game

**Authentication**: Required for development data

Show basic information about a specific game or all games. Limited by config option `game_max_age`.

#### Parameters

`game_uuid` 
: (*optional*) The unique identifier for the game.

### GET /server

**Authentication**: Required for development data. Some data may be censored if a PSK is not provided.

Shows information about active servers.

### POST /server

Add a server or 'ping' to update the server data.  `hostname` and `port` must be unique.

#### Parameters

`hostname`
: *string* The hostname or IP address of the server.

`port`
: *integer* The port number used to connect to the instance

`name`
: *string* The arbitrary name of the server.

`activePlayers`
: *integer* Current active players

`gameid`
: *string* The ID for the game currently running.  This ID is not used internally, but should be unique.

`maxPlayers`
: *integer* The maximum players that can connect to the server.

`dev`
: *boolean* Whether or not the server is a development server.

### DELETE /server

"Shutdown" a server and remove it's listing from display.

#### Parameters

**Note**: These must be URL parameters.  For example: `/server?hostname=test.foo.com&port=1234`.

`hostname`
: *string* The hostname or IP address of the server.

`port`
: *integer* The port number used to connect to the instance

### GET /game-player

**Authentication**: Required for development data. Some data may be censored if a PSK is not provided.

Shows information about players.  If no `game_player_id` is provided, detailed player information is not returned and the output is also limited by the configuration option `game_max_age`.

#### Parameters

`game_player_id`
: *integer* The ID for the unique game player.

### POST /game-player

**Authentication**: Required.

Add a game player.  This is normally done when a player connects to a server.

#### Parameters

`game_uuid`
: *uuid* The UUID of the game the player connected to.

`meta`
: *json* Meta data on a user.  This is free-form data and can include whatever you want.

### POST /game-player/stats

**Authentication**: Required.

Add game stats for a player.

#### Parameters

`game_player_id`
: *integer* The ID of the game player.

`kills`
: *integer* The amount of times the player killed another player.

`deaths`
: *integer* The amount of times the player died in a game.

### GET /leaderboard

**Authentication**: Required for development data. 

Show game stats like kills and deaths.

#### Parameters

**NOTE**: At least one parameter should be provided.  An aggregate call without parameters will be implemented but is not yet complete.

`game_player_id`
: *integer* The ID of the game player to display data for.

`game_uuid`
: *uuid* The UUID of the game you want to display data for.

`leaderboard_id`
: *integer* The ID of the specific leaderboard entry you want