"""
pygsm - A RESTful API that acts as a game server tracker

Copyright (C) 2016 GoInto, LLC

This file is part of pygsm.

pygsm is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free 
Software Foundation, either version 2 of the License, or (at your option)
any later version.

pygsm is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE.

See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with pygsm. If 
not, see <http://www.gnu.org/licenses/>.
"""
import hug
from urllib import parse
from psycopg2 import IntegrityError, ProgrammingError
from psycopg2.extras import Json
from marshmallow import fields

from core import log
from core.db import DB
from core.config import settings
from core.auth import authenticate
from utilities import response, response_positive, response_error

# setup the DB
db = DB()

# setup auth
psk_authentication = hug.authentication.api_key(authenticate)

@hug.http('/auth-test', accept=('GET', 'POST'), requires=psk_authentication)
def auth_test():
    """ Simple authentication test """
    return response_positive("Success")

@hug.get('/game', examples='game_uuid=777ab9da-bc9a-4fe5-88da-b925e44909b3')
def game(game_uuid: hug.types.uuid = None):
    """ Returns basic game information """
    if game_uuid:
        db.cursor.execute("SELECT game_uuid, stamp FROM game WHERE game_uuid=%s", [game_uuid])
    else:
        db.cursor.execute("SELECT game_uuid, stamp FROM game WHERE stamp > now() - interval '%s days'", [settings['GAME_MAX_AGE']])

    if db.cursor.rowcount > 0:

        results = []

        for row in db.cursor.fetchall():

            results.append({
                'game_uuid': str(row['game_uuid']),
                'stamp': row['stamp'].isoformat(),
                })

        return response(results)

    else:

        return response_error("No games found", 404)

@hug.get('/server')
def server(dev=False):
    """ Get active servers """

    db.cursor.execute("""SELECT ping_id, hostname, port, name, ping, 
        active, max, dev, game_uuid 
        FROM ping
        WHERE ping > now() - interval '5 minutes'
        AND down = false
        ORDER BY RANDOM()""")


    if db.cursor.rowcount > 0:

        results = []

        for row in db.cursor.fetchall():
            results.append({
                'hostname': row['hostname'],
                'port': row['port'],
                'name': row['name'],
                'ping': row['ping'],
                'activePlayers': row['active'],
                'maxPlayers': row['max'],
                'game_uuid': str(row['game_uuid']),
                })

        return response(results)

    else:

        return response_error("No servers found", 404)

@hug.post('/server', requires=psk_authentication)
def ping(hostname: hug.types.text, port: hug.types.number, 
    name: hug.types.text, activePlayers: hug.types.number, 
    game_uuid: hug.types.uuid = None, maxPlayers: hug.types.number = 8, 
    dev: hug.types.boolean = False):
    """ Add/update new server """

    log.info("ping(hostname: %s, port: %s, name: %s, activePlayers: %s, game_uuid: %s, maxPlayers: %s, dev: %s)" % (hostname, port, name, activePlayers, game_uuid, maxPlayers, dev))

    # things we'll populate later, maybe
    latest = None
    new_game = False

    # Look for previous entries for this server
    db.cursor.execute("""SELECT 
        ping_id, hostname, port, name, ping, active, max, dev, game_uuid 
        FROM ping 
        WHERE hostname = %s AND port = %s 
        AND ping > now() - interval '5 minutes'
        ORDER BY ping DESC""", 
        [hostname, port])

    if db.cursor.rowcount > 0:
        latest = db.cursor.fetchone()
        if game_uuid != latest['game_uuid']:
            new_game = True

    # if we don't already have the game_uuid, we need to get one or 
    # create one
    if not game_uuid:
        # create a new game entry
        db.cursor.execute("INSERT INTO game (stamp) VALUES (now()) RETURNING game_uuid")

        # if that was successful...
        if db.cursor.rowcount > 0:
            db.conn.commit()
            # get the game_uuid we just created
            game_uuid = db.cursor.fetchone()[0]
            
        # if it wasn't...
        else:

            # scream.
            errmsg = "Error creating new game entry."
            log.error(errmsg)
            return response_error(errmsg)
    elif new_game:
        # create a new game entry
        try:
            db.cursor.execute("INSERT INTO game (game_uuid, stamp) VALUES (%s, now()) RETURNING game_uuid", (game_uuid, ))
        except IntegrityError as e:
            log.error(str(e))
            return response_error("Could not create new game with provided game_uuid")

        # if that was successful...
        if db.cursor.rowcount > 0:
            db.conn.commit()

        # if it wasn't...
        else:

            # scream.
            errmsg = "Error creating new game entry."
            log.error(errmsg)
            return response_error(errmsg)

    # if there's not already an entry for this server...
    if not latest and game_uuid:

        # add or update one
        db.cursor.execute("""INSERT INTO ping 
            (hostname, port, name, ping, active, max, dev, game_uuid) 
            VALUES (%s, %s, %s, now(), %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT ping_hostname_port_key DO UPDATE 
            SET name = %s, ping = now(), active = %s, max = %s, dev = %s, 
            game_uuid = %s, down = false""", 
            [hostname, port, name, activePlayers, maxPlayers, dev, game_uuid,
            name, activePlayers, maxPlayers, dev, game_uuid])

        if db.cursor.rowcount < 1:
            log.error("Ping failed!")
            db.conn.rollback()
            return response_error("Ping failed for unknown reasons!")
        else:
            db.conn.commit()
            return response_positive("Ping successful!")

    else:
        db.conn.rollback()
        return response_positive("Ping uneventful!")

@hug.delete('/server')
def server(hostname: hug.types.text, port: hug.types.number):
    """ Remove an active server """

    db.cursor.execute("""UPDATE ping SET down = true 
        WHERE hostname = %s AND port = %s""", (hostname, port))


    if db.cursor.rowcount > 0:

        db.conn.commit()
        return response_positive("Shutdown successful!")

    else:

        db.conn.rollback()
        return response_error("No servers found", 404)

@hug.get('/game-player', examples="game_player_id=1")
def game_player(game_player_id: hug.types.number = None):
    """ Show player(s) and their data """

    if game_player_id:

        db.cursor.execute("""SELECT game_player_id, game_uuid, meta 
            FROM game_player gp
            WHERE game_player_id = %s""", [game_player_id])

    else:

        db.cursor.execute("""SELECT game_player_id, game_uuid
            FROM game_player gp
            JOIN game g USING (game_uuid)
            WHERE g.stamp > now() - interval '%s days'""", [settings['GAME_MAX_AGE']])

    if db.cursor.rowcount > 0:
        players = []

        for row in db.cursor.fetchall():

            players.append({
                'game_player_id': row['game_player_id'],
                'game_uuid': str(row['game_uuid']),
                })

            # Only include the in-depth data if a game_player_id was 
            # specified
            if game_player_id:
                players[-1]['meta'] = row['meta']

        return response(players)

    else:

        return response_error("No players found.", 404)

@hug.post('/game-player', requires=psk_authentication)
def add_player(game_uuid: hug.types.uuid, meta: hug.types.json):
    """ Add a player to the game """

    try:
        db.cursor.execute("""INSERT INTO game_player (game_uuid, meta) 
            VALUES (%s, %s) RETURNING game_uuid""", [game_uuid, Json(meta)])
    except IntegrityError as e:
        log.warning(str(e))
        return response_error("Invalid game_uuid provided")

    if db.cursor.rowcount < 1:
        errmsg = "Player insert failed!"
        log.error(errmsg)
        db.conn.rollback()
        return response_error(errmsg)
    else:
        db.conn.commit()
        try:
            new_player = db.cursor.fetchone()
        except ProgrammingError:
            new_player = None
        return response([{ "game_uuid": str(new_player["game_uuid"]) }, ])

@hug.get('/leaderboard')
def leaderboard(game_player_id: hug.types.number = None, game_uuid: hug.types.uuid = None, 
    leaderboard_id: hug.types.number = None):
    """ Show game stats of user(s) """

    if game_player_id:

        db.cursor.execute("""SELECT game_player_id, 
            SUM(kills) AS kills, SUM(deaths) AS deaths
            FROM leaderboard
            WHERE game_player_id = %s
            GROUP BY game_player_id""", [game_player_id])

    elif game_uuid:

        db.cursor.execute("""SELECT game_player_id, 
            SUM(kills) AS kills, SUM(deaths) AS deaths
            FROM leaderboard l
            JOIN game_player gp USING (game_player_id)
            WHERE game_uuid = %s
            GROUP BY game_player_id""", [game_uuid])

    elif leaderboard_id:

        db.cursor.execute("""SELECT game_player_id, 
            SUM(kills) AS kills, SUM(deaths) AS deaths
            FROM leaderboard l
            WHERE leaderboard_id = %s
            GROUP BY game_player_id""", [leaderboard_id])

    else:
        # TODO: aggregate display
        return response_error("Aggregate leaderboard not yet implemented.  For now, at least one parameter must be specified.", 501)

    if db.cursor.rowcount > 0:

        results = []

        for row in db.cursor.fetchall():

            results.append({
                'game_player_id': row['game_player_id'],
                'kills': row['kills'],
                'deaths': row['deaths'],
                })

        return response(results)

    else:

        return response_error("No leaderboard entries found.", 404)

@hug.post('/game-player/stats', requires=psk_authentication)
def leaderboard_add(game_player_id: hug.types.number, kills: hug.types.number, 
    deaths: hug.types.number):
    """ Add a leaderboard entry for a player """

    db.cursor.execute("""INSERT INTO leaderboard (game_player_id, kills, deaths)
        VALUES (%s, %s, %s)""", [game_player_id, kills, deaths])

    if db.cursor.rowcount < 1:
        errmsg = "Player stats insert failed!"
        log.error(errmsg)
        db.conn.rollback()
        return response_error(errmsg)
    else:
        db.conn.commit()
        return response_positive("Successfully added player stats.")

@hug.post('/register-kill', requires=psk_authentication)
def leaderboard_register_kill(alive_game_player_id: hug.types.number, 
    dead_game_player_id: hug.types.number = None):
    """ Register a kill for leaderboard update """

    # sanity check
    if not alive_game_player_id and not dead_game_player_id:
        return response_error("Invalid parameters", code=400)

    error = False
    error_code = 500
    error_messages = []

    # First, let's register the kill for the alive player

    if alive_game_player_id:

        try:

            db.cursor.execute("""INSERT INTO leaderboard (game_player_id, kills, deaths)
            VALUES (%s, %s, %s)""", [alive_game_player_id, 1, 0])

            if db.cursor.rowcount < 1:
                errmsg = "Player kill increment failed!"
                log.error(errmsg)
                db.conn.rollback()
                error = True
                error_messages.append(errmsg)
            else:
                db.conn.commit()

        except IntegrityError:
            errmsg = "Player kill increment failed! Invalid game_player_id?"
            log.error(errmsg)
            db.conn.rollback()
            error = True
            error_code = 400
            error_messages.append(errmsg)
        except Exception as e:
            log.error(str(e))
            db.conn.rollback()
            error = True
            error_messages.append(str(e))

    # Now handle the death of the dead player

    if dead_game_player_id:

        try:
        
            db.cursor.execute("""INSERT INTO leaderboard (game_player_id, kills, deaths)
            VALUES (%s, %s, %s)""", [dead_game_player_id, 0, 1])

            if db.cursor.rowcount < 1:
                errmsg = "Player death increment failed!"
                log.error(errmsg)
                db.conn.rollback()
                error = True
                error_messages.append(errmsg)
            else:
                db.conn.commit()

        except IntegrityError:
            errmsg = "Player death increment failed! Invalid game_player_id?"
            log.error(errmsg)
            db.conn.rollback()
            error = True
            error_code = 400
            error_messages.append(errmsg)
        except Exception as e:
            log.error(str(e))
            db.conn.rollback()
            error = True
            error_messages.append(str(e))
    
    if error:
        return response_error(' '.join(error_messages), code=error_code)
    else:
        return response_positive("Successfully updated player stats.")
