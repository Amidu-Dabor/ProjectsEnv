import spotipy
import requests
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

date = input("Which year do you want to travel (Type in format: YYYY-MM-DD)? ")
response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
contents = response.text
soup = BeautifulSoup(contents, "html.parser")

scope = "playlist-modify-private"
client_id = "1efbce89d811454fbebd0b8abfabc2e7"
client_secret = "aae9ded9cbda4c658dd4e361d9561faa"
redirect_uri = "https://example.com"

sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            show_dialog=True,
            cache_path="token.txt"
        )
)

user_id = sp.current_user()["id"]
top_100_songs = [song.getText().strip() for song in soup.find_all(name="h3", class_="c-title")[:100]]

spotify_song_uris = []
year = date.split("-")[0]

# Search Spotify for songs by title
for song in top_100_songs:
    uris = sp.search(q=f"track: {song} year: {year}", type="track")
    print(uris)
    try:
        uri = uris["tracks"]["items"][0]["uri"]
        spotify_song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Create a private Spotify playlist
try:
    playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
    print(playlist)
    sp.playlist_add_items(playlist_id=playlist["id"], items=spotify_song_uris)
except spotipy.exceptions.SpotifyException as e:
    print(f"Spotify API Error: {e}")


