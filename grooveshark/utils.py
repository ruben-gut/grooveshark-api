from __future__ import with_statement
"""
Grooveshark utility functions
"""
__author__ = "Tirino"

import urllib2

DOWNLOAD_CHUNK = 512 * 1024

def download_file(url, file_pointer, headers={}, data=None, progress=False):
  request = urllib2.Request(url, data, headers)
  source = urllib2.urlopen(request)
  
  downloaded = 0
  total_size = 0
  content_length = source.info().getheader('Content-Length')
  if content_length:
    total_size = int(content_length.strip())
  
  with file_pointer as dest:
    while True:
      chunk = source.read(DOWNLOAD_CHUNK)
      if not chunk:
        break
      downloaded += len(chunk)
      dest.write(chunk)
      if (progress and total_size):
        print '%s%%' % int((float(downloaded) / float(total_size)) * 100)
  return True

