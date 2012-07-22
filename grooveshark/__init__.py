"""
Unofficial Grooveshark API by Tirino - http://github.com/tirino

Inspired and based on work by:
  George Stephanos - http://github.com/jacktheripper51 (Python)
  Dan Sosedoff - http://github.com/sosedoff (Ruby)
  Daniel Lamando - http://github.com/danopia (Ruby)
"""
__author__ = "Tirino"

def test_api(username, password):
  """
  Test some of the methods of the API
  
  Your user should have at least 1 playlist
  and, ideally, some favorites
  """
  from grooveshark.client import Client
  client = Client()
  client.debug = True
  user = client.login(username, password)
  playlists = user.get_playlists()
  playlists[0].load_songs()
  song = playlists[0].songs[0]
  print song
  #for song in playlists[0].songs:
  #  print song
  #  #print client.get_song_url(song)
  #favorites = user.get_favorites()
  #for song in favorites:
  #  print song
  return user
