## make dimension tables: artist, album, genre, tracks, time, 

## Dimension tables
create_artist_table = """
CREATE TABLE IF NOT EXISTS public.dim_artist (
    artist_id VARCHAR(255) PRIMARY KEY,
    artist_name VARCHAR(255) NOT NULL,
    artist_popularity SMALLINT,
    artist_followers INTEGER,
    ingested_on VARCHAR(255)
)
"""

create_time_table = """
CREATE TABLE IF NOT EXISTS public.dim_time (
    date_id VARCHAR(255) PRIMARY KEY,
    year SMALLINT  NOT NULL,
    month SMALLINT  NOT NULL,
    day SMALLINT  NOT NULL,
    hour SMALLINT,
    minute SMALLINT, 
    second SMALLINT 
)
"""

create_albums_table = """
CREATE TABLE IF NOT EXISTS public.dim_album (
    album_id VARCHAR(255) PRIMARY KEY,
    album_name VARCHAR(255) NOT NULL,
    album_type VARCHAR(255),
    total_tracks SMALLINT, 
    release_date VARCHAR(255),
    artist_name VARCHAR(255),
    artist_id VARCHAR(255),
    ingested_on VARCHAR(255)
)
"""

create_all_tracks_table = """
CREATE TABLE IF NOT EXISTS public.dim_track (
    track_id VARCHAR(255) PRIMARY KEY,
    track_name VARCHAR(255) NOT NULL,
    duration_ms INTEGER,
    track_popularity INTEGER,
    track_uri VARCHAR(255),
    artist_name VARCHAR(255) NOT NULL,
    album_name VARCHAR(255),
    ingested_on VARCHAR(255)
)
"""

create_user_details_table = """
CREATE TABLE IF NOT EXISTS public.user_details(
    user_id VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    country VARCHAR(255),
    product VARCHAR(22)
)
"""

create_genres_table = """
CREATE TABLE IF NOT EXISTS public.dim_genre (
    genre_id INTEGER PRIMARY KEY,
    genre VARCHAR(255)
)
"""

create_artist_genre_bridge = """
CREATE TABLE IF NOT EXISTS public.dim_artist_genre_bridge (
    artist_id VARCHAR(255),
    genre_id INTEGER,
    PRIMARY KEY (artist_id, genre_id)
)
"""
create_top_songs ="""
CREATE TABLE IF NOT EXISTS public.dim_top_songs(
    rank BIGINT,
    track_name VARCHAR(255),
    track_id VARCHAR(255),
    track_uri VARCHAR(255),
    artist_name VARCHAR(255),
    artist_id VARCHAR(255),
    album_name VARCHAR(255),
    album_id VARCHAR(255),
    albun_release_date VARCHAR(255),
    duration_ms BIGINT,
    popularity SMALLINT,
    explicit BOOLEAN,
    external_url VARCHAR(255),
    ingested_on VARCHAR(255)
)
"""


## Fact tables
create_liked_songs_table = """
CREATE TABLE IF NOT EXISTS public.fact_liked_songs (
    like_id SMALLINT PRIMARY KEY,
    artist_id VARCHAR(255) NOT NULL,
    album_id VARCHAR(255),
    track_id VARCHAR(255) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE,
    time_id VARCHAR(255) NOT NULL,
    ingested_on VARCHAR(255)
)
"""

create_recently_played_table = """
CREATE TABLE IF NOT EXISTS public.fact_recently_played (
    recents_id SMALLINT PRIMARY KEY,
    track_id VARCHAR(255) NOT NULL,
    track_name VARCHAR(255) NOT NULL,
    track_uri VARCHAR(255),
    artist_name VARCHAR(255),
    artist_id VARCHAR(255),
    album_name VARCHAR(255),
    album_id VARCHAR(255),
    played_at TIMESTAMP ,
    duration_ms BIGINT,
    popularity SMALLINT,
    ingested_on VARCHAR(255) NOT NULL
)
"""


#Tables for dashboarding:

# User music preferences
create_artist_discovery = """
CREATE TABLE IF NOT EXISTS public.artist_discovery (
    artist_id VARCHAR(255) PRIMARY KEY NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    artist_populartiy SMALLINT,
    artist_followers BIGINT,
    ingested_on VARCHAR(255)
)
"""

create_artist_frequency = """
CREATE TABLE IF NOT EXISTS public.artist_frequency(
    artist_name VARCHAR(255) NOT NULL,
    like_count SMALLINT
)
"""

create_genre_analysis = """
CREATE TABLE IF NOT EXISTS public.genre_analysis(
    genres VARCHAR(255) NOT NULL,
    genre_count SMALLINT
)
"""

create_monthly_genre_trend = """
CREATE TABLE IF NOT EXISTS public.monthly_genre_trend(
    month_year VARCHAR(7) NOT NULL
            CHECK (month_year ~ '^\d{4}-\d{2}$'),
    genres VARCHAR(255) NOT NULL,
    genre_count SMALLINT
)
"""


create_monthly_likes = """
CREATE TABLE IF NOT EXISTS public.monthly_likes(
    month_year VARCHAR(7) NOT NULL
            CHECK (month_year ~ '^\d{4}-\d{2}$'),
    monthly_like_count SMALLINT
)
"""

create_song_details = """
CREATE TABLE IF NOT EXISTS public.song_details(
    track_name VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255),
    album_name VARCHAR(255),
    duration_ms BIGINT,
    artists_popularity FLOAT,
    added_at TIMESTAMP
)
"""




# Recent plays analysis

create_recent_tracks_by_popularity =  """
CREATE TABLE IF NOT EXISTS public.recent_tracks_by_popularity(
    track_name VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    popularity SMALLINT
)
"""
create_daily_plays =  """
CREATE TABLE IF NOT EXISTS public.daily_plays(
    date DATE NOT NULL,
    play_count SMALLINT
)
"""

create_recent_play_genre_analysis = """
CREATE TABLE IF NOT EXISTS public.recent_plays_genre_analysis(
    genres VARCHAR(255) NOT NULL,
    count SMALLINT
)
"""

create_recent_play_summary = """
CREATE TABLE IF NOT EXISTS public.recent_plays_summary(
    metric VARCHAR(255) NOT NULL,
    value DOUBLE PRECISION
)
"""

create_recent_play_top_artists = """
CREATE TABLE IF NOT EXISTS public.recent_plays_top_artists(
    artist_name VARCHAR(255) NOT NULL,
    play_count SMALLINT,
    artist_popularity SMALLINT
)
"""