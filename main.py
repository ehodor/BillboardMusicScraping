from pprint import pprint
from requests.exceptions import ReadTimeout
from bs4 import BeautifulSoup
import requests
import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USERNAME = os.getenv('USERNAME')
SPOTIPY_REDIRECT_URI=os.getenv('SPOTIPY_REDIRECT_URI')
user_input = input("What week in the last 20 years would you like music from? Format: YYYY-MM-DD\n")

billboard_url = f'https://www.billboard.com/charts/hot-100/{user_input}/'

spotipy_response = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope='playlist-modify', cache_path='access.txt', username=USERNAME, show_dialog=True, requests_timeout=30 ))
#spotipy_response = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=SPOTIPY_REDIRECT_URI, scope='playlist-modify-private')
#spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

#headers = requests.utils.default_headers()

response = requests.get(url=billboard_url)
webpage = response.text

soup = BeautifulSoup(webpage, "html.parser")

song_titles = soup.select(selector="li ul li h3")
song_artists = soup.select(selector="div div ul li ul li span")
titles = [title.getText().strip() for title in song_titles]

artists =[artist.getText().strip() for artist in song_artists if (not artist.getText().strip().isnumeric() and artist.getText().strip() != "-")]

results = []
for i in range(len(song_titles)):
    #print(f"current artist: {artists[i]}\n")
    query = titles[i] + ' ' + artists[i]
    try:
        entry = spotipy_response.search(q=query, limit=1)
    except ReadTimeout:
        print("Spotify API timed out, trying query again.")
        entry = spotipy_response.search(q=query, limit=1)
    try:
        entry = entry['tracks']['items'][0]['uri']
        results.append(entry)
    except IndexError:
        print('Song could not be found on Spotify, moving on to next song.')
user = spotipy_response.current_user()['id']
new_playlist = spotipy_response.user_playlist_create(user=user, name=f'{user_input} Billboard Top 100')
try:
    spotipy_response.user_playlist_add_tracks(user=user, playlist_id=new_playlist['id'], tracks=results)
except ReadTimeout:
    print("Spotify API timed out, trying query again.")
    spotipy_response.user_playlist_add_tracks(user=user, playlist_id=new_playlist['id'], tracks=results)
