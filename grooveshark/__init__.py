"""
Unofficial Grooveshark API by Tirino - http://github.com/tirino

Inspired and based on work by:
  George Stephanos - http://github.com/jacktheripper51 (Python)
  Dan Sosedoff - http://github.com/sosedoff (Ruby)
  Daniel Lamando - http://github.com/danopia (Ruby)
"""
__author__ = "Tirino"

def cli_test(username, password):
  from grooveshark.client import Client
  client = Client()
  client.debug = True
  user = client.login(username, password)
  playlists = user.get_playlists()
  for song in playlists[0].load_songs():
    print song
    print client.get_song_url(song)
  return user
