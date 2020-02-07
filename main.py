# Get Artist URI
name = "Cannibal Corpse"

artist_uri = get_artist_uri(name)

artist_albums = get_artist_albums(artist_uri)
print(artist_albums)
print("Total albums:", len(full_tracklist))

# Manually clean some entries, we want original albums only and no live performances
albums_to_delete = ['レッド・ビフォー・ブラック', 
                     'Vile (Expanded Edition)', 
                     'The Bleeding - Reissue',
                     'Live Cannibalism',
                     'Torturing And Eviscerating',
                   ]

artist_albums_uri = get_clean_album_uri_list(artist_albums, albums_to_delete)

full_tracklist = get_full_tracklist_dict(artist_albums_uri)
print("Total tracks:", len(full_tracklist))

audio_features_dict = get_audio_features_dict(full_tracklist)