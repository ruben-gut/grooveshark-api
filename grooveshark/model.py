"""
Grooveshark models
"""
__author__ = "Tirino"

class Song(object):
  def __init__(self, data=None):
    self.data = data
    if data:
      self.id = data['SongID']
      self.name = data['Name']
      if 'SongNameID' in data:
        self.name_id = data['SongNameID']
      else:
        self.name_id = None
      self.artist = data['ArtistName']
      self.artist_id = data['ArtistID']
      self.album = data['AlbumName']
      self.album_id = data['AlbumID']
      self.track = data['TrackNum']
      self.duration = data['EstimateDuration']
      self.artwork = data['CoverArtFilename']
      self.popularity = data['Popularity']
      if 'Year' in data:
        self.year = data['Year']
      else:
        self.year = None
    else:
      self.id = None
      self.name = None
      self.name_id = None
      self.artist = None
      self.artist_id = None
      self.album = None
      self.album_id = None
      self.track = None
      self.duration = None
      self.artwork = None
      self.popularity = None
      self.year = None
  
  def get_artwork_url(self, tiny=False):
    size = '70' if tiny else '90'
    return 'http://images.grooveshark.com/static/albums/%s_%s' % (size, self.artwork)
  
  def __str__(self):
    return ' - '.join([str(self.id), self.name, self.artist])
  
  def to_dict(self):
    return {
      'songID': self.id,
      'songName': self.name,
      'artistName': self.artist,
      'artistID': self.artist_id,
      'albumName': self.album,
      'albumID': self.album_id,
      'track': self.track
    }

class Playlist(object):
  def __init__(self, client, data=None, user_id=None):
    self.client = client
    self.data = data
    self.songs = []
    if data:
      self.id = data['PlaylistID']
      self.name = data['Name']
      self.about = data['About']
      self.picture = data['Picture']
      if 'UserID' in data:
        self.user_id = data['UserID']
      else:
        self.user_id = user_id
      self.uuid = data['UUID']
    else:
      self.user_id = user_id
  
  def load_songs(self):
    """Fetch playlist songs"""
    songs = self.client.request('playlistGetSongs', {'playlistID': self.id})['Songs']
    for song in songs:
      self.songs.append(Song(song))
  
  def rename(self, name, description):
    """Rename this playlist"""
    try:
      self.client.request('renamePlaylist', {'playlistID': self.id, 'playlistName': name})
      self.client.request('setPlaylistAbout', {'playlistID': self.id, 'about': self.description})
      self.name = name
      self.about = description
      return True
    except:
      return False
  
  def delete(self):
    """Delete this playlist"""
    return self.client.request('deletePlaylist', {'playlistID': self.id, 'name': self.name})

  def __str__(self):
    return ' - '.join([str(self.id), self.name, '%s songs' % len(self.songs)])

