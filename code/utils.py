import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import credentials  # file containing API credentials for spotify / genius

# Import credentials and instantiate client with authorization
SPOTIPY_CLIENT_ID = credentials.client_id
SPOTIPY_CLIENT_SECRET = credentials.client_secret

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, 
                                                      client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_artist_uri(name):
    """Look up artist URI from artist name. If multiple results are found,
    return first URI."""

    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    artist_uri = items[0]['uri']
    return artist_uri


def get_artist_albums(artist_uri):
    """Return a dict of albums for the respective albums.
    Setting title as key catches some duplicates."""
    albums = {}
    results = sp.artist_albums(artist_uri, album_type='album')
    for i, item in enumerate(results['items']):
        albums[item['name'].title()] = item['uri']
    return albums


def get_clean_album_uri_list(artist_albums, albums_to_delete=albums_to_delete):
    """Remove some albums according to a list of ablum names (if you wish)."""
    if albums_to_delete is not None:
        for key in albums_to_delete:
            artist_albums.pop(key)
    artist_albums_uri = [uri for uri in artist_albums.values()]
    return artist_albums_uri


def get_full_tracklist_dict(artist_albums_uri):
    """For every album get the tracks and concatenate them all.
    Setting title as key catches some duplicates."""
    tracklist = {}
    for album_uri in artist_albums_uri:
        album = sp.album(album_uri)
        for track in album['tracks']['items']:
            tracklist[track['name'].title()] = track['uri']
    return tracklist


def get_audio_features_dict(full_tracklist):
    """Get the audio features (energy, valence) for every track in the tracklist."""
    audio_features_dict = {}
    for uri in list(full_tracklist.values()):
        features = sp.audio_features(uri)
        audio_features_dict[uri] = {'energy': features[0]['energy'],
                                    'valence': features[0]['valence'],
                                   }
    return audio_features_dict


temp_df1 = pd.DataFrame(full_tracklist.items(), columns = ['title', 'uri'])
temp_df2 = pd.DataFrame(audio_features_dict.items(), columns = ['uri', 'features'])
assert len(temp_df1) == len(temp_df2)
song_data = pd.merge(temp_df1, temp_df2, on=['uri'])
display(song_data.head(2))


song_data['energy'] = song_data['uri'].apply(lambda x: audio_features_dict[x]['energy'])
song_data['valence'] = song_data['uri'].apply(lambda x: audio_features_dict[x]['valence'])
song_data['danceability'] = song_data['uri'].apply(lambda x: audio_features_dict[x]['danceability'])
song_data.drop('features', axis=1, inplace=True)

# Calculate "Sonic Brutality Index"
def calc_sbi(valence, energy):
    sbi = ((1 - valence) + energy) / 2
    return sbi
   
song_data['sbi'] = song_data.apply(lambda x: calc_sbi(x['valence'], x['energy']), axis=1)
song_data[['title', 'sbi']].nlargest(5, 'sbi')


# Check for (musically) most brutal song

most_brutal_uri = song_data['uri'].loc[song_data['sbi'] == song_data['sbi'].max()].values[0]
results = sp.track(most_brutal_uri)
print('track       : ' + results['name'])
print('from ablbum : ' + results['album']['name'])
print('audio       : ' + results['preview_url'])
print('cover art   : ' + results['album']['images'][0]['url'])


def get_duration(list_of_song_uri):
    duration_dict = {}
    for song_uri in list_of_song_uri:
        results = sp.track(song_uri)
        duration_dict[song_uri] = results['duration_ms']
        
    return duration_dict


duration_dict = get_duration(full_tracklist.values())
song_data['duration_sec'] = song_data['uri'].apply(lambda x: duration_dict[x] / 1000)  # values are in ms
display(song_data.head(2))


## Save data
song_data.to_csv('data/processed/audio_data.csv', index=False)

# Retrieve data from API




name2 = "Cannabis Corpse"

artist_uri2 = get_artist_uri(name2)
artist_albums2 = get_artist_albums(artist_uri2)
artist_albums_uri2 = get_clean_album_uri_list(artist_albums2, albums_to_delete=None)
full_tracklist2 = get_full_tracklist_dict(artist_albums_uri2)
audio_features_dict2 = get_audio_features_dict(full_tracklist2)
pprint(list(audio_features_dict2.items())[:2])
print("\nTotal Number of songs:", len(audio_features_dict2))


# %%
# Construct DataFrame
temp_df1 = pd.DataFrame(full_tracklist2.items(), columns = ['title', 'uri'])
temp_df2 = pd.DataFrame(audio_features_dict2.items(), columns = ['uri', 'features'])
assert len(temp_df1) == len(temp_df2)
song_data2 = pd.merge(temp_df1, temp_df2, on=['uri'])

song_data2['energy'] = song_data2['uri'].apply(lambda x: audio_features_dict2[x]['energy'])
song_data2['valence'] = song_data2['uri'].apply(lambda x: audio_features_dict2[x]['valence'])
song_data2['danceability'] = song_data2['uri'].apply(lambda x: audio_features_dict2[x]['danceability'])
song_data2.drop('features', axis=1, inplace=True)


# %%
# Calculae SBI
song_data2['sbi'] = song_data2.apply(lambda x: calc_sbi(x['valence'], x['energy']), axis=1)
display(song_data2.head(2))


# %%
# Compare Brutality of Cannibal Corpse and Cannabis Corpse
print(f"Mean Brutality Score for {name}: {song_data['sbi'].mean():.2f}")
print(f"Mean Brutality Score for {name2}: {song_data2['sbi'].mean():.2f}")
