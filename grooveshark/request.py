"""
Grooveshark Request base calss
"""
__author__ = "Tirino"

import gzip
import hashlib
import httplib
try:
  import simplejson as json
except ImportError:
  import json
import StringIO
import time
import uuid

API_BASE = 'grooveshark.com'
UUID = str(uuid.uuid4()).upper()
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.11 ' \
             '(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
CLIENT = 'htmlshark'
CLIENT_REV = '20120220.01'
SALT = ':jayLikeWater:'

COUNTRY = {'CC1': 0, 'CC2': 0, 'CC3': 0, 'CC4': 0, 'ID': 1, 'DMA': 0, 'IPR':0}
REFERER = "http://grooveshark.com/JSQueue.swf?%s" % CLIENT_REV
TOKEN_TTL = 120 # 2 minutes

# Client overrides for different methods
METHOD_CLIENTS = {'getStreamKeysFromSongIDs': 'jsqueue'}
METHOD_SALTS = {'getStreamKeysFromSongIDs': ':bangersAndMash:'}

class Request(object):
  def __init__(self):
    self.comm_token = None
    self.comm_token_ttl = None
    self.debug = False
  
  def _build_comm_token(self):
    """Get and assign communication token"""
    self.comm_token = None # cleanup or we'll be in trouble
    self.comm_token = self.request('getCommunicationToken', 
      {'secretKey': hashlib.md5(self.session).hexdigest()}, True
    )
    self.comm_token_ttl = int(time.time())
 
  def request(self, method, params={}, secure=False):
    """Perform API request"""
    if self.comm_token:
      self.refresh_token()

    client = METHOD_CLIENTS[method] if method in METHOD_CLIENTS else CLIENT
    body = {
      'header': {
        'session': self.session,
        'uuid': UUID,
        'client': client,
        'clientRevision': CLIENT_REV,
        'privacy': 0,
        'country': COUNTRY
      },
      'method': method,
      'parameters': params
    }
    if self.comm_token:
      body['header']['token'] = self._create_token(method)
    
    headers = {
      'User-Agent': USER_AGENT, 
      'Referer': REFERER,
      'Accept-Encoding': 'gzip',
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': 'PHPSESSID=%s' % self.session
    }
    try:
      if secure:
        conn = httplib.HTTPSConnection(API_BASE)
      else:
        conn = httplib.HTTPConnection(API_BASE)
      
      if self.debug:
        print ">> Request API Method: %s" % method
        print ">> Request Headers: %s" % headers
        print ">> Request Parameters: %s" % body
      
      conn.request(
        'POST', '/more.php?%s' % method, 
        json.dumps(body), headers=headers
      )
      resp = conn.getresponse()
    except Exception, ex:
      raise Exception('Could not make request: %s' % str(ex))
    
    resp_data = gzip.GzipFile(
      fileobj=(StringIO.StringIO(resp.read()))
    ).read()
    
    if self.debug:
      print "<< Response Headers: %s" % resp.getheaders()
      print "<< Response Status: %s, Reason: %s" % (resp.status, resp.reason)
      print "<< Response Data: %s" % resp_data
      print ""
    
    data = json.loads(resp_data)
    if 'fault' in data:
      raise Exception(data['fault'])
    else:
      return data['result']

  def refresh_token(self):
    """Refresh communications token if TTL has passed"""
    if ((time.time() - self.comm_token_ttl) > TOKEN_TTL):
      self._build_comm_token()

