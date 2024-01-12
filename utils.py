import re
from configparser import ConfigParser

import psycopg2


def config(filename='database.ini', section='postgresql'):
    """takes secret login info from database.ini to be used to connect to postgres"""
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def commit_to_dataBase(query):
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute(query)
        conn.commit()
        cur.close()



    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        # close the communication with the PostgreSQL


    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def commit_to_dataBase2(query):
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute(query)
        conn.commit()
        cur.close()



    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        # close the communication with the PostgreSQL


    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def call_club_data(query):
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute(query)
        #conn.commit()
        cur.close()



    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        # close the communication with the PostgreSQL


    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def extract_from_dataBase(query):
    """ Connect to the PostgreSQL database server to allow for artist names to be inputed to
    spotify api search"""
    conn = None

    try:
        # read connection parameters
        params = config()
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        cur.execute(query)
        result = cur.fetchall()
        artdict = {}

        for i in result:
            x = i[1].split(',')
            artdict[i[0]] = x

        conn.commit()
        cur.close()



    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        # close the communication with the PostgreSQL


    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return artdict


def name_cleaner(name):
    """Cleans unwanted words and icons from names scraped"""
    
    if pd.notnull(name):
        name = re.sub('\\n', ',', name)
        name = re.sub(r'\broom|ROOM\b', 'room:,', name)
        name = re.sub('(\\xa0)', '', name)
        name = re.sub(r'\bTBA|tba\b', '', name)
        name = re.sub('(noch nicht fetsgelegt)', '', name)
        name = re.sub(r'\b(Friends|friends)\b', '', name)
        name = re.sub(r'\b(opening|Opening|OPENING)\b', '', name)
        name = re.sub(r'\b(closing|Closing|CLOSING)\b', '', name)
        name = re.sub(r'\bResidents|residents\b', '', name)
        name = re.sub(r'\bResident|resident\b', '', name)
        name = re.sub(r'\b(\d\d\s\-\d\d)\b', '', name)
        name = re.sub(r'\b(\d\d\-\d\d)\b', '', name)
        name = re.sub(r'\b(\d\d\-\s\d\d)\b', '', name)
        name = re.sub(r'(\_{2}[a-zA-Z]*\_{2})', '', name)
        name = re.sub(r'\blive|LIVE|Live\b', ',', name)
        name = re.sub(r"\(.*?\)", ',', name)
        name = re.sub(r'\&', ',', name)
        name = re.sub(r'\[.*?\]', '', name)
        name = re.sub(r'[\s\w]+\:', '', name)
        name = re.sub(r'\/{2}', ',', name)
        name = re.sub(r'\,{2}', ',', name)
        name = re.sub(r'\,{2}', ',', name)
        name = re.sub(r'\'{2},', '', name)
        name = re.sub(r'^,', '', name)
        name = re.sub(r'^\s', '', name)
        name = re.sub(r'\s$', '', name)
        name = re.sub(r'\b\d{2}\b', '', name)
        name = re.sub(r'\bb2b|B2B\b', ',', name)
        name = re.sub(r'w\/', ',', name)
        name = re.sub(r'\+', ',', name)
        name = re.sub(r'\&', ',', name)  # & symbol, replace with ','
        name = re.sub(r'[,\s]*$', '', name)  # white space & comma from end of string
        name = re.sub(r'^@', '', name)  # @ from the beginning of str
        djList = name.split(',')
        return name
    return ''

def clean_names(names):
    cleaned_names = []
    for name in names:
        cleaned_name = ''.join(c for c in name if c.isalnum() or c == "'" or c.isspace())
        cleaned_name = cleaned_name.strip()
        if cleaned_name:
            cleaned_names.append(cleaned_name)
    return cleaned_names


def tag_cleaner(tags):
    tags = ','.join("'" + item + "'" for item in tags)
    tags = tags.lower()
    tags = re.sub(r'[/&]',',',tags)
    tags = re.sub(r'[^a-z\,\-\s]','',tags)
    tags = tags.split(',')
    tags = [tag.strip() for tag in tags]
    tags = ','.join("'" + tag + "'" for tag in tags)
    return tags



def remove_emojis(text):
    """to remove emojis from names scraped---not working"""
    # Compile the emoji pattern
    emoji_pattern = re.compile('['
                               u'\U0001F600-\U0001F64F'  # emoticons
                               u'\U0001F300-\U0001F5FF'  # symbols & pictographs
                               u'\U0001F680-\U0001F6FF'  # transport & map symbols
                               u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                               ']+', flags=re.UNICODE)
    # Use the regex to remove the emojis
    return emoji_pattern.sub(r'', text)

disabled_evasions = ['chrome_app',
        'chrome_runtime',
        'iframe_content_window',
        'media_codecs',
        'sourceurl',
        'navigator_hardware_concurrency',
        'navigator_languages',
        'navigator_permissions',
        'navigator_plugins',
        'navigator_vendor',
        'navigator_webdriver',
        'user_agent_override',
        'webgl_vendor',
        'window_outerdimensions']

create_artists_table = """CREATE TABLE IF NOT EXISTS artists (
artist_id SERIAL,
artist_name VARCHAR(150) PRIMARY KEY,
spotify_uri VARCHAR(70),
soundcloud_link VARCHAR(200),
bandcamp_link VARCHAR(200),
facebook_link VARCHAR(200),
instagram_link VARCHAR(200),
other_link VARCHAR(200),
ra_link VARCHAR(255),
genres TEXT[],
email TEXT UNIQUE,
website TEXT);
"""

create_events_table = """CREATE TABLE IF NOT EXISTS event_data(
event_id SERIAL,
event_name VARCHAR(256) PRIMARY KEY,
club_name VARCHAR(256),
club_address VARCHAR(300),
event_date DATE,
start_time TIME,
end_time TIME,
artists TEXT[],
popularity INTERGER(6),
price VARCHAR(30)
event_genres TEXT[]
);
"""

merge_genre_query = """UPDATE event_data
    SET event_genres = subquery2.event_genres
    FROM (
      SELECT event_name, array_agg(genre) AS event_genres
      FROM (
        SELECT event_name, unnest(unique_genres) AS genre
        FROM (
          SELECT event_name, array_agg(distinct genre) AS unique_genres
          FROM event_data, unnest(event_genres) AS genre
          GROUP BY event_name, genre
        ) AS subquery
        GROUP BY event_name, unique_genres
      ) AS subquery2
      GROUP BY event_name
    ) AS subquery2
    WHERE event_data.event_name = subquery2.event_name;"""
