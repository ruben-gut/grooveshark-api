"""
Grooveshark Client interface
"""
__author__ = "Tirino"

import datetime

from grooveshark.model import Song, Playlist

class User(object):
  def __init__(self, client, data=None):
    """Init user account object"""
    self.data = data
    if data:
      self.id = data['userID']
      self.username = data['username']
      self.premium = data['isPremium']
      self.email = data['Email']
      self.city = data['City']
      self.country = data['Country']
      self.sex = data['Sex']
    else:
      self.id = None
      self.username = None
      self.premium = None
      self.email = None
      self.city = None
      self.country = None
      self.sex = None
    self.client = client
    self.playlists = []
    self.favorites = []

  def get_avatar(self):
    """Get user avatar URL"""
    return "http://beta.grooveshark.com/static/userimages/%s.jpg" % self.id
  
  def get_feed(self, date=None):
    """Get user activity for the date (Comes as RAW response)"""
    if not date:
      date = datetime.datetime.now()
    return self.client.request('getProcessedUserFeedData', {'userID': self.id, 'day': date.strftime("%Y%m%d")})
  
  # User Library #
  
  def get_library(self, page=0):
    """Fetch songs from library"""
    songs = self.client.request('userGetSongsInLibrary', {'userID': self.id, 'page': str(page)})['songs']
    for song in songs:
      yield Song(song)
  
  def library_add(self, songs=[]):
    """Add songs to user's library"""
    songs_data = []
    for song in songs:
      songs_data.append(song.to_dict())
    return self.client.request('userAddSongsToLibrary', {'songs': songs_data})
  
  def library_remove(self, song):
    """Remove song from library"""
    return self.client.request('userRemoveSongFromLibrary', 
      {'userID': self.id, 'songID': song.id, 'albumID': song.album_id, 'artistID': song.artist_id}
    )
  
  def library_ts_modified(self):
    return self.client.request('userGetLibraryTSModified', {'userID': self.id})
  
  # User Playlists #
  
  def get_playlists(self):
    """Fetch user playlists"""
    if not self.playlists:
      results = self.client.request('userGetPlaylists', {'userID': self.id})['Playlists']
      for playlist in results:
        self.playlists.append(Playlist(self.client, playlist, self.id))
    return self.playlists
  
  def get_playlist(self, playlist_id):
    """Get a playlist by ID"""
    result = None
    playlists = self.get_playlists()
    for playlist in playlists:
      if (playlist.id == playlist_id):
        result = playlist
        break
    return result
  
  def create_playlist(self, name, description='', songs=[]):
    """Create new user playlist"""
    song_ids = []
    for song in songs:
      if (isinstance(song, Song)):
        song_ids.append(song.id)
      else:
        song_ids.append(str(song))
    return self.client.request('createPlaylist', {
      'playlistName': name,
      'playlistAbout': description,
      'songIDs': song_ids
    })
  
  # User Favorites #
  
  def get_favorites(self):
    """Get user favorites"""
    if not self.favorites:
      results = self.client.request('getFavorites', {'ofWhat': 'Songs', 'userID': self.id})
      for song in results:
        self.favorites.append(Song(song))
    return self.favorites
  
  def add_favorite(self, song):
    """Add song to favorites"""
    song_id = song.id if isinstance(song, Song) else str(song)
    return self.client.request('favorite', {'what': 'Song', 'ID': song_id})
  
  def remove_favorite(self, song):
    """Remove song from favorites"""
    song_id = song.id if isinstance(song, Song) else str(song)
    return self.client.request('unfavorite', {'what': 'Song', 'ID': song_id})

