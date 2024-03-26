import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Spotify API credentials - REPLACE WITH YOUR CREDENTIALS
client_id = '23f5b5ae10874e0d9db993f3e9d532ec'
client_secret = '68407a217ae24d57b888c4e1ba6a2f29'


# Initialize Spotipy with Spotify Client Credentials
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def search_spotify(album=None, artist=None, track=None, year=None, genre=None, tag=None,num=5):
    query_components = []
    if album:
        query_components.append(f"album:{album}")
    if artist:
        query_components.append(f"artist:{artist}")
    if track:
        query_components.append(f"track:{track}")
    if year:
        query_components.append(f"year:{year}")
    if genre:
        query_components.append(f"genre:{genre}")
    # if tag:
    #     query_components.append(f"tag:{tag}")

    query = " ".join(query_components)
    if not query:
        return pd.DataFrame()  # Return an empty DataFrame if no query parameters

    results = sp.search(query, type='track', limit=num)

    tracks_info = []
    track_ids = []
    for item in results['tracks']['items']:
        # Collect track IDs to request their audio features
        track_ids.append(item['id'])
        track_info = {
            'id': item['id'],  # Ensure the 'id' is included here for joining later
            'Track Name': item['name'],
            'Artist': ", ".join(artist['name'] for artist in item['artists']),
            'Album': item['album']['name'],
            'Release Date': item['album']['release_date'],
            'Popularity': item['popularity'],
            'Spotify Link': item['external_urls']['spotify']
        }
        tracks_info.append(track_info)

    df_tracks = pd.DataFrame(tracks_info)
    
    if track_ids:
        features_list = [features for features in sp.audio_features(track_ids) if features]
        if features_list:
            features_df = pd.DataFrame(features_list)
            # Filter out any rows that might not have the expected structure
            if 'id' in features_df:
                selected_features = features_df[['id', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
                df_tracks = pd.merge(df_tracks, selected_features, on='id', how='left')
            else:
                st.error("Failed to retrieve track features.")
        else:
            st.warning("No audio features found for the tracks.")

    return df_tracks

# Read genres from CSV
def get_genres_from_csv(file_path='genres.csv'):
    try:
        genres_df = pd.read_csv(file_path)
        genres_list = genres_df['Genre'].tolist()
    except FileNotFoundError:
        st.sidebar.error(f"File not found: {file_path}")
        genres_list = []
    return genres_list

# Streamlit UI
st.set_page_config(page_icon="🎧", page_title="Music Search")

st.title("Song Search")

# Sidebar for search form
with st.sidebar:
    st.header("Search Parameters")
    with st.form("search_form"):
        genres = get_genres_from_csv()  # Load genres from CSV
        genre = st.selectbox("Genre", [''] + genres)  # Add the genres to the selectbox, prepend with empty string for optional selection
        track = st.text_input("Track")
        artist = st.text_input("Artist")
        album = st.text_input("Album")
        years = list(range(1900, 2025))  # Example range from 1900 to current year
        year = st.selectbox("Year", [''] + years)  # Add years to the selectbox, prepend with empty string for optional selection
        num = st.slider('Number of tracks', 0, 50, 25)
        st.write("Look for ", num, 'tracks')

        submitted = st.form_submit_button("Search")
    # tag = st.text_input("Tag", disabled=True)

if submitted:
    df_results = search_spotify(album=album, artist=artist, track=track, year=year, genre=genre, num=num)

    df_results=df_results[['Track Name','Artist','Popularity','Spotify Link','Release Date','Album','danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
    st.dataframe(
        df_results,
        column_config={
            "name": "Track",
            "Popularity": st.column_config.NumberColumn(
                "Popularity",
                help="Popularity Ranking",
                format="%d 🔥",
            ),
            "Spotify Link": st.column_config.LinkColumn("Spotify",display_text="Listen 🎧"),
        },
        hide_index=True,
    )


else:
    st.success('Choose at least one parameter on the left to see results', icon="🎧")
