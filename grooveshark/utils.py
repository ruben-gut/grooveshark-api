"""
Grooveshark utility functions
"""
__author__ = "Tirino"

import urllib2

DOWNLOAD_CHUNK = 512 * 1024

def download_file(url, filename, headers={}, data=None):
  request = urllib2.Request(url, data, headers)
  source = urllib2.urlopen(request)
  
  downloaded = 0
  total_size = 0
  content_length = source.info().getheader('Content-Length')
  if content_length:
    total_size = int(content_length.strip())
  
  with open(filename, 'wb') as dest:
    while True:
      chunk = source.read(DOWNLOAD_CHUNK)
      if not chunk:
        break
      downloaded += len(chunk)
      dest.write(chunk)
      if total_size:
        # print progress
        print '%s%' int((float(downloaded) / float(total_size)) * 100)
  return True

