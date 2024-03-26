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

def search_spotify(album=None, artist=None, track=None, year=None, genre=None, tag=None):
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
    if tag:
        query_components.append(f"tag:{tag}")

    query = " ".join(query_components)
    if not query:
        return pd.DataFrame()  # Return an empty DataFrame if no query parameters
    
    results = sp.search(query, type='track', limit=50)
    
    tracks_info = []
    for item in results['tracks']['items']:
        track_info = {
            'Track Name': item['name'],
            'Artist': ", ".join(artist['name'] for artist in item['artists']),
            'Album': item['album']['name'],
            'Release Date': item['album']['release_date'],
            'Popularity': item['popularity'],
            'Spotify Link': item['external_urls']['spotify']  # Add the Spotify link to the track
        }
        tracks_info.append(track_info)

    return pd.DataFrame(tracks_info)

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
        tag = st.text_input("Tag")
        submitted = st.form_submit_button("Search")

if submitted:
    df_results = search_spotify(album=album, artist=artist, track=track, year=year, genre=genre, tag=tag)
    
    # # Display the DataFrame without the 'Spotify Link' column to avoid redundancy
    # st.dataframe(df_results.drop(columns=['Spotify Link']))
    # # Display a header for the links section
    # st.subheader("Spotify Links")
    df_results=df_results[['Track Name','Artist','Popularity','Spotify Link','Release Date','Album']]
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
    # for index, row in df_results.iterrows():
    #     link = f"[{row['Track Name']}]({row['Spotify Link']})"
    #     st.markdown(link, unsafe_allow_html=True)

else:
    st.success('Choose at least one parameter on the left to see results', icon="🎧")
