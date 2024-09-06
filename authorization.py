import os
from datetime import datetime, timedelta
import sqlite3

import requests
import spotipy
from spotipy import SpotifyOAuth
from dotenv import load_dotenv
import psycopg2
load_dotenv()


ADMIN_ID = str(os.getenv("ADMIN_ID"))
CLIENT_ID = str(os.getenv("CLIENT_ID"))
CLIENT_SECRET = str(os.getenv("CLIENT_SECRET"))
main_url = "http://bitesaitzz.pythonanywhere.com"
DATABASE_URL = os.environ['DATABASE_URL']

class autorizationSpot:

    def add_user(self, message):
        print("Add user")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        name = message.from_user.first_name
        username = message.from_user.username
        user_id = str(message.from_user.id)
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        for el in users:
            if (el[2] == username):
                cur.close()
                conn.close()
                return
        print(name, username, user_id)

        cur.execute(
            "INSERT INTO users (name, username, user_id, access_token, refresh_token, expires_in) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, username, user_id, None, None, None))
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users_access')
        users = cur.fetchall()
        for el in users:
            if (el[2] == username):
                cur.close()
                conn.close()
                return
        cur.execute(
            "INSERT INTO users_access (user_id, username, email) VALUES (%s,%s,%s)",
            (user_id, username, None))
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users_listened')
        users = cur.fetchall()
        for el in users:
            print("TEST users_listened: ", el[1], " ", username)
            if (el[1] == username):
                cur.close()
                conn.close()
                return
        cur.execute(
            "INSERT INTO users_listened (user_id, track_id, play_count) VALUES (%s,%s,%s) ON CONFLICT (user_id, track_id)"
            " DO UPDATE SET play_count = users_listened.play_count + EXCLUDED.play_count",
            (user_id, 0, 0))
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('SELECT * FROM weekly_users_listened')
        users = cur.fetchall()
        for el in users:
            if (el[1] == username):
                cur.close()
                conn.close()
                return
        cur.execute(
            "INSERT INTO weekly_users_listened (user_id, track_id, play_count) VALUES (%s,%s,%s)",
            (user_id, 0, 0))
        conn.commit()
        cur.close()
        conn.close()

    def createDB(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print("Created db!")
        cur = conn.cursor()
        cur.execute('''
                      CREATE TABLE IF NOT EXISTS users (
                          id SERIAL PRIMARY KEY,
                          name TEXT,
                          username TEXT,
                          user_id TEXT,
                          access_token TEXT,
                          refresh_token TEXT,
                          expires_in TIMESTAMP
                         
                      )
                  ''')
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('''
                        CREATE TABLE IF NOT EXISTS users_access (
                            id SERIAL PRIMARY KEY,
                            user_id TEXT,
                            username TEXT,
                            email TEXT
                            )
                    ''')
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('''
                        CREATE TABLE IF NOT EXISTS users_listened (
                user_id TEXT,
                track_id TEXT,
                play_count INTEGER,
                time TIMESTAMP,
                PRIMARY KEY (user_id, track_id)
                            )
                    ''')
        cur.execute('''
                               CREATE TABLE IF NOT EXISTS weekly_users_listened (
                       user_id TEXT,
                       track_id TEXT,
                       play_count INTEGER,
                       time TIMESTAMP,
                       PRIMARY KEY (user_id, track_id)
                                   )
                           ''')
        conn.commit()
        cur.close()
        conn.close()

    def deleteWeekListened(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DELETE FROM weekly_users_listened')
        conn.commit()
        cur.close()
        conn.close()
    def deleteListened(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DELETE FROM users_listened')
        conn.commit()
        cur.close()
        conn.close()
    def deleteAccess(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DELETE FROM users_access')
        conn.commit()
        cur.close()
        conn.close()
    def deleteData(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DELETE FROM users')
        conn.commit()
        cur.close()
        conn.close()

    def deleteTables(self):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DROP TABLE users')
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DROP TABLE users_access')
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DROP TABLE users_listened')
        conn.commit()
        cur.close()
        conn.close()

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('DROP TABLE weekly_users_listened')
        conn.commit()
        cur.close()
        conn.close()
    def delete_cache(self, user_id):
        cache_file = f'.cache-"{user_id}"'
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"Cache file {cache_file} has been deleted.")
        else:
            print("The cache file does not exist.")
    def checkIfUser(self, username_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE user_id = '{username_id}'")
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user == None:
            return False
        else:
            return True
    def checkIfLogin(self, username_id):
        if (self.checkIfAccess(username_id) == False):
            return False

        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE user_id = '{username_id}'")
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user[4] == None:
            return False
        else:
            return True

    def checkIfAccess(self, user_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')


        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users_access WHERE user_id = '{user_id}'")
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user[3] == None:


            return False
        else:
            return True

    def checkExpired(self, expires_in):
        #expires_in_datetime = datetime.strptime(expires_in, '%Y-%m-%d %H:%M:%S.%f')
        if isinstance(expires_in, str):
            expires_in_datetime = datetime.strptime(expires_in, '%Y-%m-%d %H:%M:%S.%f')
        elif isinstance(expires_in, datetime):
            expires_in_datetime = expires_in
        else:
            print("Unexpected type for expires_in:"+ expires_in + " - "+type(expires_in))
            return False

        now = datetime.now() + timedelta(hours=2)
        print(f"ckeck time: {expires_in_datetime} || {now}")
        if expires_in_datetime < now:
            print("true")
            return True
        else:
            print("false")
            return False

    def add_access_db(self, id, email):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users_access')
        cur.execute(f"UPDATE users_access SET email = '{email}' WHERE user_id = '{id}'")
        conn.commit()
        cur.close()
        conn.close()

    def get_token_refresh_expired(self, username_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')


        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE user_id = '{username_id}'")
        user = cur.fetchone()

        access_token = user[4]
        refresh_token = user[5]
        expires_in = user[6]
        cur.close()
        conn.close()
        return access_token, refresh_token, expires_in

    def save_token(self, token_info, username_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        cur.execute(
            f"UPDATE users SET access_token = '{token_info['access_token']}', refresh_token = '{token_info['refresh_token']}',"
            f" expires_in = '{datetime.now() +timedelta(hours=2)+ timedelta(seconds=token_info['expires_in'])}' "
            f"WHERE user_id = '{username_id}'")
        conn.commit()
        cur.close()
        conn.close()

    def refresh_token(self, username_id, ref_token):
        print(f"{datetime.now()+timedelta(hours=2)}-- refreshed token -- {str(username_id)}")
        if (self.checkIfLogin(username_id) == False):
            return
        #self.delete_cache(username_id)
        sp_oauth = self.create_spoty_oauth(username_id)
        try:
            token_info = sp_oauth.refresh_access_token(ref_token)
            self.save_token(token_info, username_id)
        except:
            return None

        #print(f"{datetime.now()}-- new token -- {str(username_id)} ||| {token_info}")
        return token_info

    def create_spoty_oauth(self, username_id):
        scope = "user-top-read playlist-read-private playlist-read-collaborative playlist-modify-public " \
                "user-library-read user-read-recently-played user-read-playback-state"
        cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'caches')

        os.makedirs(cache_dir, exist_ok=True)  # Ensure the directory exists
        cache_path = os.path.join(cache_dir, f".cache-{username_id}")
        print(f"{datetime.now()}-- created spoty_oauth -- {str(username_id)} ||| {cache_path}")

        return SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=f"{main_url}/callback", scope=scope,
            username=username_id,
            cache_path=cache_path)
    def checkIfEmail(self, email):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users_access WHERE email = '{email}'")
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user == None:
            return False
        else:
            return True
    def deleteFromLoggined(self, id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor()
        cur.execute(f"UPDATE users SET access_token = NULL, refresh_token = NULL, expires_in = NULL WHERE user_id = '{id}'")
        conn.commit()
        cur.close()
        conn.close()
    def deleteFromAccess(self, id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"UPDATE users_access SET email = NULL WHERE user_id = '{id}'")
        conn.commit()
        cur.close()
        conn.close()

    def get_sp_token(self, user_id):
        token, ref_token, expires_in = self.get_token_refresh_expired(user_id)
        print(f'{datetime.now()}-- get sp_token -- "{str(user_id)}"')

        if self.checkExpired(expires_in) == True:
            #print(f"{datetime.now()}-- token expired -- {str(user_id)}")
            token_info = self.refresh_token(user_id, ref_token)
            if token_info == None:
                return None
            token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
        sp._session = requests.Session()
        sp._session.timeout = 5
        print('well done get_sp_token')
        return sp
    def get_all_users(self):
        print(f'"{datetime.now()}"-- get all users --')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT user_id FROM users_access')
        users = cur.fetchall()
        cur.close()
        conn.close()
        checked_users = []
        for user in users:
            if(self.checkIfLogin(user[0]) and user[0] == ADMIN_ID):
                checked_users.append(user)
        return checked_users

    def add_listened_track(self, username_id, listened_tracks):
        time = datetime.now()
        print(f'"{datetime.now()}"-- added tracks to users_listened -- {str(username_id)}')
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        for track in listened_tracks:
            how_many_times_plays = listened_tracks[track]
            cur.execute(f"SELECT * FROM users_listened WHERE user_id = '{username_id}' AND track_id = '{track}'")
            tracks = cur.fetchone()

            # Perform the same operations for the week_users_listened table
            cur.execute(f"SELECT * FROM weekly_users_listened WHERE user_id = '{username_id}' AND track_id = '{track}'")
            week_tracks = cur.fetchone()

            if tracks == None:
                cur.execute(
                    "INSERT INTO users_listened (user_id, track_id, play_count, time) VALUES (%s,%s,%s, %s)",
                    (username_id, track, how_many_times_plays, time))
            else:
                cur.execute(
                    f"UPDATE users_listened SET play_count = play_count + {how_many_times_plays}, time = '{time}' "
                    f"WHERE user_id = '{username_id}' AND track_id = '{track}'")

            # Perform the same operations for the week_users_listened table
            if week_tracks == None:
                cur.execute(
                    "INSERT INTO weekly_users_listened (user_id, track_id, play_count, time) VALUES (%s,%s,%s, %s)",
                    (username_id, track, how_many_times_plays, time))
            else:
                cur.execute(
                    f"UPDATE weekly_users_listened SET play_count = play_count + {how_many_times_plays}, time = '{time}' "
                    f"WHERE user_id = '{username_id}' AND track_id = '{track}'")

        conn.commit()
        cur.close()
        conn.close()

    def get_listened_tracks(self, username_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print(f'"{datetime.now()}"-- got tracks from users_listened -- "{str(username_id)}"')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users_listened WHERE user_id = '{username_id}'")
        tracks = cur.fetchall()
        cur.close()
        conn.close()
        return tracks
    def get_listened_weekly_tracks(self, username_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print(f'"{datetime.now()}"-- got tracks from users__weekl -- "{str(username_id)}"')

        cur = conn.cursor()
        cur.execute(f"SELECT * FROM weekly_users_listened WHERE user_id = '{username_id}'")
        tracks = cur.fetchall()
        cur.close()
        conn.close()
        return tracks

    def get_size_listened(self, username_id):
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM users_listened WHERE user_id = '{username_id}'")
        size = cur.fetchone()
        cur.close()
        conn.close()
        return size[0]
