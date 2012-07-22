"""
Grooveshark Client interface
"""
__author__ = "Tirino"

import hashlib
import httplib
import random
import re
import time

from grooveshark.model import Song, Playlist
from grooveshark.request import Request, SALT, METHOD_SALTS
from grooveshark.request import REFERER, USER_AGENT, COUNTRY
from grooveshark.user import User
from grooveshark import utils

SESSION_END_POINT = 'grooveshark.com'

MAX_CLOSE_URL_REQUESTS = 2
WAIT_BETWEEN_URL_REQUESTS = 60 # seconds

class Client(Request):
  def __init__(self, session=None):
    Request.__init__(self)
    self.user = None
    self.session = session or self._get_session()
    self.last_song_url_request = 0
    self.close_song_url_requests = 0
    self._build_comm_token()
  
  def _get_session(self):
    """Obtain new session from Grooveshark"""
    conn = httplib.HTTPConnection(SESSION_END_POINT) 
    conn.request('HEAD', '', headers={'User-Agent': USER_AGENT}) 
    resp = conn.getresponse()
    match = re.search(
      'PHPSESSID=([a-z\d]{32});', 
      resp.getheader("set-cookie")
    )
    return match.group(1)
   
  def _create_token(self, method):
    """Sign method"""
    rnd = '%06x' % random.randrange(256, 256**3)
    salt = METHOD_SALTS[method] if method in METHOD_SALTS else SALT
    plain = "%s:%s%s%s" % (method, self.comm_token, salt, rnd)
    hashed = hashlib.sha1(plain).hexdigest()
    return "%s%s" % (rnd, hashed)
  
  def login(self, username, password):
    """Authenticate user"""
    data = self.request('authenticateUser', 
      {'username': username, 'password': password}, True
    )
    self.user = User(self, data)
    if not self.user.id:
      raise Exception("Invalid username/password.")
    return self.user

  def find_user_by_id(self, id_):
    resp = self.request('getUserByID', {'userID': id_})['user']
    return User(self, resp) if resp['username'] else None
  
  def get_user_by_username(self, username):
    """Find user by username"""
    resp = self.request('getUserByUsername', {'username': username})['user']
    return User(self, resp) if resp['username'] else None
  
  def get_recent_users(self):
    """Get recently active users"""
    users = self.request('getRecentlyActiveUsers', {})['users']
    for user in users:
      yield User(self, user)
  
  def get_popular_songs(self, type_='daily'):
    """
    Get popular songs
    type_ => daily, monthly
    """
    if type_ not in ['daily', 'monthly']:
      raise Exception('Invalid type: %s' % type_)
    else:
      result = self.request('popularGetSongs', {'type': type_})
      for song in result['songs']:
        yield Song(song)
  
  def search(self, type_, query):
    """Perform search request for query"""
    result = self.request('getSearchResults', 
      {'type': type_, 'query': query}
    )
    for song in result['songs']:
      yield Song(song)
  
  def search_songs(self, query):
    """Perform songs search request for query"""
    return self.search('Songs', query)
  
  def search_songs_pure(self, query):
    """Return raw response for songs search request"""
    return self.request('getSearchResultsEx', 
      {'type': 'Songs', 'query': query}
    )
  
  def get_stream_auth_by_song_id(self, song_id):
    """Get stream authentication by song ID"""
    now = time.time()
    if not self.last_song_url_request: # first request
      self.close_song_url_requests = 1
    else:
      self.close_song_url_requests = self.close_song_url_requests + 1
    
    if (self.close_song_url_requests > MAX_CLOSE_URL_REQUESTS):
      if (self.last_song_url_request + WAIT_BETWEEN_URL_REQUESTS < now):
        raise Exception('You cannot make URL requests that often! ' \
                        'Grooveshark will notice something\'s not right.')
      else: # we're good, enough time has passed, let's clean up
        self.close_song_url_requests = 1
        self.last_song_url_request = now
    else: # we're good
      # check if we can reset the counter
      if (self.last_song_url_request + WAIT_BETWEEN_URL_REQUESTS > now):
         # enough time has passed since the last request, let's clean up
         self.close_song_url_requests = 1
      self.last_song_url_request = now
    
    return self.request('getStreamKeysFromSongIDs', {
      'mobile': 'false',
      'prefetch': 'false',
      'songIDs': song_id,
      'country': COUNTRY
    })
  
  def get_stream_auth(self, song):
    """Get stream authentication for song object"""
    return self.get_stream_auth_by_song_id(song.id)
  
  def get_song_url_by_id(self, song_id):
    """Get song stream url by ID"""
    resp = self.get_stream_auth_by_song_id(song_id)
    song_id = str(song_id)
    if song_id in resp and resp[song_id]:
      data = resp[song_id]
    else:
      raise Exception('Uh-oh! Received empty data!')
    
    return "http://%s/stream.php?streamKey=%s" % (
      data['ip'], data['streamKey']
    )
  
  def get_song_url(self, song):
    """Get song stream"""
    return self.get_song_url_by_id(song.id)
  
  def download_song(self, song, output_folder='./'):
    """Download a song to a specific folder or the current one (default)"""
    headers = {'User-Agent': USER_AGENT, 'Referer': REFERER}
    output = '%s%s - %s.mp3' % (output_folder, song.artist, song.name)
    return utils.download_file(self.get_song_url(song), output, headers)

