# Import libraries
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import credentials  # file where API credentials for spotify / genius are stored


# Import credentials and instantiate client with authorization

SPOTIPY_CLIENT_ID = credentials.client_id
SPOTIPY_CLIENT_SECRET = credentials.client_secret

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, 
                                                      client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# %% [markdown]
# ## Request data from the Spotify API
# 
# ### Artist

# %%
# Get Artist URI

name = "Cannibal Corpse"

def get_artist_uri(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    artist_uri = items[0]['uri'] 
    return artist_uri


# %%
artist_uri = get_artist_uri(name)
pprint(artist_uri)

# %% [markdown]
# ### Trackslist
# 
# The easiest way to query for tracks is as follows:
# 
# ```python
# results = sp.search(q=artist, limit=50, type='track')
# for i, t in enumerate(results['tracks']['items']):
#     print(' ', i, t['name'])
# ```
# 
# But as the upper limit per request is 50 songs, and CC have released many more than that, so I work around by requesting a list of all their albums, clean it a bit, and then combine all the tracks in one big tracklist.

# %%
# Get Artist albums (dict)
# Note: setting title as key catches some duplicates

def get_artist_albums(artist_uri):
    albums = {}
    results = sp.artist_albums(artist_uri, album_type='album')
    for i, item in enumerate(results['items']):
        albums[item['name'].title()] = item['uri']
    return albums


# %%
artist_albums = get_artist_albums(artist_uri)
pprint(artist_albums)


# %%
# Manually clean some entries, we want original albums only and no live performances
albums_to_delete = ['レッド・ビフォー・ブラック', 
                     'Vile (Expanded Edition)', 
                     'The Bleeding - Reissue',
                     'Live Cannibalism',
                     'Torturing And Eviscerating',
                   ]
def get_clean_album_uri_list(artist_albums, albums_to_delete=albums_to_delete):
    if albums_to_delete is not None:
        for key in albums_to_delete:
            artist_albums.pop(key)  
    artist_albums_uri = [uri for uri in artist_albums.values()]
    return artist_albums_uri


# %%
artist_albums_uri = get_clean_album_uri_list(artist_albums, albums_to_delete)
print(artist_albums_uri)


# %%
# Get the full tracklist
def get_full_tracklist_dict(artist_albums_uri):
    tracklist = {}
    for album_uri in artist_albums_uri:
        album = sp.album(album_uri)
        for track in album['tracks']['items']:
            tracklist[track['name'].title()] = track['uri']
    return tracklist


# %%
full_tracklist = get_full_tracklist_dict(artist_albums_uri)
print(list(full_tracklist.items())[0])
print("Total tracks:", len(full_tracklist))

# %% [markdown]
# ### Audio Features
# 
# We use the audio features provided by spotify ([see here](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)) to determine the sonic brutality of a track. We actually only need `Energy`and `Valence` for that, but in addition let's also have a look at the `Dancability`of Cannibal Corpse. Just for fun.
# 
# > Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
#     
# > Valence is a measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry). 
#     
# > Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity.

# %%
def get_audio_features_dict(full_tracklist):
    audio_features_dict = {}
    for uri in list(full_tracklist.values()):
        features = sp.audio_features(uri)
        audio_features_dict[uri] = {'energy': features[0]['energy'],
                                    'valence': features[0]['valence'],
                                    'danceability': features[0]['danceability'],
                                   }
    return audio_features_dict


# %%
audio_features_dict = get_audio_features_dict(full_tracklist)
pprint(list(audio_features_dict.items())[:2])

# %% [markdown]
# ## Analyse Songs
# 
# ### Prepare dataframe
# 
# Getting the songs and features in separate dicts was ok for exploring the Spotify API and Spotipy wrapper, but for our the actual Analyis I prefer to combine everything in a dataframe.

# %%
temp_df1 = pd.DataFrame(full_tracklist.items(), columns = ['title', 'uri'])
temp_df2 = pd.DataFrame(audio_features_dict.items(), columns = ['uri', 'features'])
assert len(temp_df1) == len(temp_df2)
song_data = pd.merge(temp_df1, temp_df2, on=['uri'])
display(song_data.head(2))


# %%
song_data['energy'] = song_data['uri'].apply(lambda x: audio_features_dict[x]['energy'])
song_data['valence'] = song_data['uri'].apply(lambda x: audio_features_dict[x]['valence'])
song_data['danceability'] = song_data['uri'].apply(lambda x: audio_features_dict[x]['danceability'])
song_data.drop('features', axis=1, inplace=True)


# %%
display(song_data.head(2))


# %%
fig, axes = plt.subplots(nrows=1, ncols=3, sharex=True, figsize=(16,4))
sns.distplot(song_data['valence'], ax=axes[0])
sns.distplot(song_data['energy'], ax=axes[1])
sns.distplot(song_data['danceability'],color="grey", ax=axes[2])

axes[0].set_xlabel('Valence', fontsize='large')
axes[1].set_xlabel('Energy', fontsize='large')
axes[2].set_xlabel('Danceability', fontsize='large')
axes[0].set_ylabel('Frequency', fontsize='large');


# %%
# Check for outlier with energy value of approx. 0.8 only
# And get link to a 30 sek sample

low_energy_uri = song_data['uri'].loc[song_data['energy'] == song_data['energy'].min()].values[0]
results = sp.track(low_energy_uri)
print('track       : ' + results['name'])
print('from ablbum : ' + results['album']['name'])
print('audio       : ' + results['preview_url'])
print('cover art   : ' + results['album']['images'][0]['url'])

# %% [markdown]
# ### Calculate "Sonic Brutality Index"
# 
# Using both `energy` and `valence`, we can create an equation for the “Sonic Brutality Index” by calculating the arithmetic mean of `energy` and `1 - valence` (subtracting valence from 1 so that a higher value means it’s more “negative”). This way, the most brutal songs will be those that are both high in energy and low in valence, while equally weighting both.
# 
# $$\\Sonic Brutality Index = \frac{(1 - valence) + energy}{2}$$

# %%
def calc_sbi(valence, energy):
    sbi = ((1 - valence) + energy) / 2
    return sbi
    
song_data['sbi'] = song_data.apply(lambda x: calc_sbi(x['valence'], x['energy']), axis=1)
display(song_data.head(2))


# %%
fig, ax = plt.subplots(figsize=(8,4))
sns.distplot(song_data['sbi'], bins=20, label="Sonic Brutaliy Index")

ax.set_title('Distribution of sbi for 144 songs', fontsize=14)
ax.set_xlabel('Sonic Brutality Index', fontsize='large')
ax.set_ylabel('Frequency', fontsize='large');


# %%
song_data[['title', 'sbi']].nlargest(5, 'sbi')


# %%
# Check for (musically) most brutal song 

most_brutal_uri = song_data['uri'].loc[song_data['sbi'] == song_data['sbi'].max()].values[0]
results = sp.track(most_brutal_uri)
print('track       : ' + results['name'])
print('from ablbum : ' + results['album']['name'])
print('audio       : ' + results['preview_url'])
print('cover art   : ' + results['album']['images'][0]['url'])

# %% [markdown]
# Youtube-Clip: 
# 
# <a href="http://www.youtube.com/watch?feature=player_embedded&v=57WwWg9PD74
# " target="_blank"><img src="http://img.youtube.com/vi/57WwWg9PD74/0.jpg" 
# alt="Link to Youtube clip" width="240" height="180" border="10" /></a>

# %%
# For comparision: Lets listen to a not so brutal but danceable track now
# (don't expect too much though ...)

rabid_uri = song_data['uri'].loc[song_data['title'] == 'Rabid'].values[0]
results = sp.track(rabid_uri)
print('track       : ' + results['name'])
print('from ablbum : ' + results['album']['name'])
print('audio       : ' + results['preview_url'])
print('cover art   : ' + results['album']['images'][0]['url'])

# %% [markdown]
# Before we save the data and go on, we will first append the duration of each song to the dataframe. This is something we'll need for the calculation of the "Lyrical Brutality Index" in the next notebook.

# %%
def get_duration(list_of_song_uri):
    duration_dict = {}
    for song_uri in list_of_song_uri:
        results = sp.track(song_uri)
        duration_dict[song_uri] = results['duration_ms']
        
    return duration_dict


# %%
duration_dict = get_duration(full_tracklist.values())
song_data['duration_sec'] = song_data['uri'].apply(lambda x: duration_dict[x] / 1000)  # values are in ms
display(song_data.head(2))


# %%
## Save data
song_data.to_csv('data/processed/audio_data.csv', index=False)

# %% [markdown]
# ---
# %% [markdown]
# ## Appendix: Compare Sonic Brutality of Cannibal Corpse and Cannabis Corpse
# 
# [Cannabis Corpse](https://en.wikipedia.org/wiki/Cannabis_Corpse) started out as some kind of parody of bands like Cannibal Corpse (obviously), Obituary, Death ... But meanwhile they have been around for about 13 years  and six albums. Besides of deserving credit for still finding death metal songs to make pot jokes about, I think they have developed into one of the most consistent death metal bands in general, writing really good music.(And they are a super funny live band!)

# %%
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


# %%
plt.figure(figsize=(8,4))
sns.distplot(song_data['sbi'], bins=20, label=name);
sns.distplot(song_data2['sbi'], color='yellow', bins=20, label=name2);
plt.legend(loc='upper left');

# %% [markdown]
# The original is just about a bit more brutal than the 'tribute band'. But not by much ... Cannabis Corpse definitely come very close.

# %%
# Check-out most brutal Cannabis Corpse song
most_brutal_uri2 = song_data2['uri'].loc[song_data2['sbi'] == song_data2['sbi'].max()].values[0]
results = sp.track(most_brutal_uri2)
print('track       : ' + results['name'])
print('from ablbum : ' + results['album']['name'])
print('audio       : ' + results['preview_url'])
print('cover art   : ' + results['album']['images'][0]['url'])


# %%
song_data2.nlargest(1, 'sbi')

# %% [markdown]
# ---
