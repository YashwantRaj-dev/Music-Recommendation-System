import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_id = 'b255ad668fa049409df33cf9d78dbe2b'
client_secret = 'e53ac673cc6e4ccc914e04934dbbca74'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_song_info(song_name):
    # Search for a track
    results = sp.search(q=f'track:{song_name}', type='track', limit=1)

    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        song_name = track['name']
        artist_name = track['artists'][0]['name']
        #release_date = track['album']['release_date']

        # Retrieving lyrics is more complex and typically requires other services or APIs

        return {
            'song_name': song_name,
            'artist_name': artist_name,
            #'release_date': release_date,
        }
    else:
        return None

def search_songs(query):
    results = sp.search(q=query, type='track', limit=10)
    return results['tracks']['items']


song_info = get_song_info('Song Name')
if song_info:
    print(song_info)
else:
    print('Song not found.') 