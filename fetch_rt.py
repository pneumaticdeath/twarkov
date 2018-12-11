#!/usr/bin/env python

import time
from tweetdb import textof
from users import sharon

def getRT(tw):
  orig_tw = tw
  while hasattr(tw, 'retweeted_status') and tw.retweeted_status:
    tw = tw.retweeted_status
  if orig_tw.id != tw.id:
    return tw
  else:
    return None

if __name__ == '__main__':
  rts = sharon.chain._tweetstore.matching('RT')
  for x in rts:
    if x.text[:2] == 'RT':
      try:
        real = sharon.chain.GetApi().GetStatus(x.id)
        newrt = getRT(real)
        if newrt:
          print('Replacing @{}: {}'.format(x.user.screen_name.encode('utf-8'), x.text.encode('utf-8')))
          print(' With @{}: {}'.format(newrt.user.screen_name.encode('utf-8'), textof(newrt).encode('utf-8')))
          sharon.chain._tweetstore.add(newrt)
          del sharon.chain._tweetstore[x.id]
      except Exception as e:
        print('Error fetching @{}: {}    {}'.format(x.user.screen_name.encode('utf-8'), x.text.encode('utf-8'), str(e)))
      time.sleep(1)





