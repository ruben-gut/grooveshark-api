#!/usr/bin/env python
"""
A Grooveshark API based on work by George Stephanos <gaf.stephanos@gmail.com>
By tirino.wok@gmail.com
"""

import httplib
import StringIO
import hashlib
import uuid
import random
import string
import sys
import os
import subprocess
import gzip
try:
  import json
except:
  import simplejson as json

CLIENT_NAME = "htmlshark"
CLIENT_REVISION = "20120220"
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
REFERER = "http://grooveshark.com/JSQueue.swf?%s.01" % CLIENT_REVISION
END_POINT = "grooveshark.com"

class GSharkAPI(object):

  def __init__(self):
    self.token = None
    self._build_headers()

    conn = httplib.HTTPConnection(END_POINT)
    conn.request("HEAD", "", headers={"User-Agent": USER_AGENT})
    res = conn.getresponse()
    cookie = res.getheader("set-cookie").split(";")
    self.headers_data["session"] = cookie[0][10:]

  def _build_headers(self):
    self.headers_data = {}
    self.headers_data["country"] = {}
    self.headers_data["country"]["CC1"] = "0"
    self.headers_data["country"]["CC2"] = "0"
    self.headers_data["country"]["CC3"] = "0"
    self.headers_data["country"]["CC4"] = "0"
    self.headers_data["country"]["ID"] = "1"
    self.headers_data["privacy"] = 0
    self.headers_data["session"] = None
    self.headers_data["uuid"] = str(uuid.uuid4()).upper()

  def _response_as_json(self, conn):
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())

  def getToken(self):
    params = {}
    params["parameters"] = {}
    params["parameters"]["secretKey"] = hashlib.md5(self.headers_data["session"]).hexdigest()
    params["method"] = "getCommunicationToken"
    params["header"] = self.headers_data
    params["header"]["client"] = CLIENT_NAME
    params["header"]["clientRevision"] = CLIENT_REVISION

    conn = httplib.HTTPSConnection(END_POINT)
    conn.request("POST", "/more.php", json.JSONEncoder().encode(params), 
      {"User-Agent": USER_AGENT, "Referer": REFERER, "Content-Type":"", "Accept-Encoding":"gzip", 
      "Cookie":"PHPSESSID=" + self.headers_data["session"]}
    )
    self.token = self._response_as_json(conn)["result"]
    #print self.token

  def prepToken(self, method, secret):
    rnd = (''.join(random.choice(string.hexdigits) for x in range(6))).lower()
    return rnd + hashlib.sha1(method + ":" + self.token + secret + rnd).hexdigest()

  def getResultsFromSearch(self, query, what="Songs"):
    params = {}
    params["parameters"] = {}
    params["parameters"]["type"] = what
    params["parameters"]["query"] = query
    params["header"] = self.headers_data
    params["header"]["client"] = CLIENT_NAME
    params["header"]["clientRevision"] = CLIENT_REVISION
    params["header"]["token"] = self.prepToken("getResultsFromSearch", ":jayLikeWater:")
    params["method"] = "getResultsFromSearch"
    conn = httplib.HTTPConnection(END_POINT)
    conn.request("POST", "/more.php?" + params["method"], json.JSONEncoder().encode(params), 
      {"User-Agent": USER_AGENT, "Referer":"http://grooveshark.com/", "Content-Type":"application/json", 
        "Accept-Encoding":"gzip", "Cookie":"PHPSESSID=" + self.headers_data["session"]}
    )
    resp = self._response_as_json(conn)
    print resp
    try:
        return resp["result"]["result"]["Songs"]
    except:
        return resp["result"]["result"]

  def artistGetSongsEx(self, id_, isVerified):
    params = {}
    params["parameters"] = {}
    params["parameters"]["artistID"] = id_
    params["parameters"]["isVerifiedOrPopular"] = isVerified
    params["header"] = self.headers_data
    params["header"]["client"] = CLIENT_NAME
    params["header"]["clientRevision"] = CLIENT_REVISION
    params["header"]["token"] = self.prepToken("artistGetSongsEx", ":jayLikeWater:")
    params["method"] = "artistGetSongsEx"
    conn = httplib.HTTPConnection(END_POINT)
    conn.request("POST", "/more.php?" + params["method"], json.JSONEncoder().encode(params),
      {"User-Agent": USER_AGENT, "Referer": REFERER, "Content-Type":"", "Accept-Encoding":"gzip", 
        "Cookie":"PHPSESSID=" + self.headers_data["session"]}
    )
    return self._response_as_json(conn)

  def getStreamKeyFromSongIDEx(self, id):
    params = {}
    params["parameters"] = {}
    params["parameters"]["mobile"] = "false"
    params["parameters"]["prefetch"] = "false"
    params["parameters"]["songIDs"] = id
    params["parameters"]["country"] = self.headers_data["country"]
    params["header"] = self.headers_data
    params["header"]["client"] = "jsqueue"
    params["header"]["clientRevision"] = "%s.01" % CLIENT_REVISION
    params["header"]["token"] = self.prepToken("getStreamKeysFromSongIDs", ":bangersAndMash:")
    params["method"] = "getStreamKeysFromSongIDs"
    conn = httplib.HTTPConnection(END_POINT)
    conn.request("POST", "/more.php?" + params["method"], json.JSONEncoder().encode(params), 
      {"User-Agent": USER_AGENT, "Referer": REFERER, "Accept-Encoding":"gzip", "Content-Type":"", 
        "Cookie":"PHPSESSID=" + self.headers_data["session"]}
    )
    return self._response_as_json(conn)

  def header_cb(self, buf):
    if "PHPSESSID" in buf:
      buf = buf.split(' ')
      self.headers_data["session"] = buf[1][10:-1]

  def doDownload(self, stream, song_data):
    if (os.uname()[0] == 'Darwin'):
      cmd = 'curl --user-agent "%s" --referer "%s" -d streamKey=%s -o "%s - %s.mp3" "http://%s/stream.php"' % (
        USER_AGENT, REFERER, stream["streamKey"], song_data["ArtistName"], song_data["SongName"], stream["ip"]) 
    else:
      cmd = 'wget --user-agent="%s" --referer=%s --post-data=streamKey=%s -O "%s - %s.mp3" "http://%s/stream.php"' % (
        USER_AGENT, REFERER, stream["streamKey"], song_data["ArtistName"], song_data["SongName"], stream["ip"])
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()

def cli_ui(query):
  api = GSharkAPI()
  api.getToken()
  song_nbr = 0
  search_results = api.getResultsFromSearch(query)
  for song_data in search_results:
    song_nbr += 1
    print "%s: '%s' by %s (%s)" % (song_nbr, song_data['SongName'], song_data['ArtistName'] , song_data['AlbumName'])
    if song_nbr == 10:
      break

  song_id = raw_input("Enter the Song ID you wish to download or (q) to exit: ")
  if (not song_id or song_id == "q"):
    exit()
  else:
    song_id = int(song_id) - 1
    song_data = search_results[song_id]
    stream = api.getStreamKeyFromSongIDEx(song_data["SongID"])
    for key, value in stream['result'].iteritems():
      print "key: %s, value: %s" % (key, value)
      stream = value
    api.doDownload(stream, song_data)

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "Please enter a search criteria"
    exit()
  else:
    cli_ui(sys.argv[1])

