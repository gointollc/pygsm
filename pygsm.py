import hug, log
from psycopg2.extras import Json
from marshmallow import fields
from db import DB
from utilities import response, response_positive, response_error
from config import settings

# setup the DB
db = DB()

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
                })

        return response(results)

    else:

        return response_error("No servers found", 404)

@hug.post('/server')
def ping(hostname: hug.types.text, port: hug.types.number, 
    name: hug.types.text, activePlayers: hug.types.number, 
    gameid: hug.types.text, maxPlayers: hug.types.number = 8, 
    dev: hug.types.boolean = False):
    """ Add/update new server """

    # things we'll populate later, maybe
    latest = None
    game_uuid = None

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
        game_uuid = latest['game_uuid']

    # if we don't already have the game_uuid, we need to get one or 
    # create one
    if not game_uuid:

        # Get the game_uuid
        db.cursor.execute("SELECT game_uuid FROM game WHERE game_id = %s", [gameid])

        # if it doesn't exist...
        if db.cursor.rowcount < 1:

            # create a new game entry
            db.cursor.execute("INSERT INTO game (game_uuid, game_id, stamp) VALUES (uuid_generate_v4(), %s, now()) RETURNING game_uuid", [gameid])

            # if that was successful...
            if db.cursor.rowcount > 0:

                # get the game_uuid we just created
                game_uuid = db.cursor.fetchone()[0]

            # if it wasn't...
            else:

                # scream.
                errmsg = "Error creating new game entry."
                log.error(errmsg)
                return response_error(errmsg)

        # if it does exist...
        else:

            # get the game_uuid
            game_uuid = db.cursor.fetchone()[0]

    # if there's not already an entry for this server...
    if not latest:

        # add one
        db.cursor.execute("""INSERT INTO ping 
            (hostname, port, name, ping, active, max, dev, game_uuid) 
            VALUES (%s, %s, %s, now(), %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT ping_hostname_port_key DO UPDATE 
            SET name = %s, ping = now(), active = %s, max = %s, dev = %s, 
            game_uuid = %s""", 
            [hostname, port, name, activePlayers, maxPlayers, dev, game_uuid,
            name, activePlayers, maxPlayers, dev, game_uuid])

    # otherwise, let's update the record
    else:

        db.cursor.execute("")

    if db.cursor.rowcount < 1:
        log.error("Ping failed!")
        db.conn.rollback()
        return response_error("Ping failed for unknown reasons!")
    else:
        db.conn.commit()
        return response_positive("Ping successful!")

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

@hug.post('/game-player')
def add_player(game_uuid: hug.types.uuid, meta: hug.types.json):
    """ Add a player to the game """

    db.cursor.execute("""INSERT INTO game_player (game_uuid, meta) 
        VALUES (%s, %s)""", [game_uuid, Json(meta)])

    if db.cursor.rowcount < 1:
        errmsg = "Player insert failed!"
        log.error(errmsg)
        db.conn.rollback()
        return response_error(errmsg)
    else:
        db.conn.commit()
        return response_positive("Successfully added player.")

@hug.get('/leaderboard')
def leaderboard(game_player_id: hug.types.number = None, game_uuid: hug.types.uuid = None, 
    leaderboard_id: hug.types.number = None):
    """ Show game stats of user(s) """

    if game_player_id:

        db.cursor.execute("""SELECT leaderboard_id, game_player_id, 
            kills, deaths 
            FROM leaderboard
            WHERE game_player_id = %s""", [game_player_id])

    elif game_uuid:

        db.cursor.execute("""SELECT leaderboard_id, game_player_id, 
            kills, deaths 
            FROM leaderboard l
            JOIN game_player gp USING (game_player_id)
            WHERE game_uuid = %s""", [game_uuid])

    elif leaderboard_id:

        db.cursor.execute("""SELECT leaderboard_id, game_player_id, 
            kills, deaths 
            FROM leaderboard l
            WHERE leaderboard_id = %s""", [leaderboard_id])

    else:
        # TODO: aggregate display
        return response_error("Aggregate leaderboard not yet implemented.  For now, at least one parameter must be specified.", 501)

    if db.cursor.rowcount > 0:

        results = []

        for row in db.cursor.fetchall():

            results.append({
                'leaderboard_id': row['leaderboard_id'],
                'game_player_id': row['game_player_id'],
                'kills': row['kills'],
                'deaths': row['deaths'],
                })

        return response(results)

    else:

        return response_error("No leaderboard entries found.", 404)

@hug.post('/game-player/stats')
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