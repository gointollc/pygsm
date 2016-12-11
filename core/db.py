import psycopg2, psycopg2.extensions, psycopg2.extras

from core import log
from core.config import settings


class DB:
    """ Handles database functions """
    
    conn = None
    cursor = None

    def __init__(self):
        self.connect()
        psycopg2.extras.register_uuid()
        psycopg2.extras.register_default_jsonb(self.conn)

    def connect(self):
        """ Connect to the database """

        self.conn = psycopg2.connect(
            database    = settings['DB_NAME'],
            user        = settings['DB_USER'],
            password    = settings['DB_PASS'],
            host        = settings['DB_HOST'],
            port        = settings['DB_PORT']
        )

        if self.conn.status != psycopg2.extensions.STATUS_READY:
            # oops
            log.error("ERROR: Database connection failed!")
        else:
            # get the cursor
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        return self.conn