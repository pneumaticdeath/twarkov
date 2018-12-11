#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from tweetdb import textof
from users import sharon


if __name__ == '__main__':
  replaced = 0
  errors = 0
  processed = 0
  trunc_tw = sharon.chain._tweetstore.matching('…'.decode('utf-8'))
  for x in trunc_tw:
    try:
      real = sharon.chain.GetApi().GetStatus(x.id)
      processed += 1
      if real.text != x.text:
        print('Replacing @{}: {}'.format(x.user.screen_name.encode('utf-8'), x.text.encode('utf-8')))
        print(' With @{}: {}'.format(real.user.screen_name.encode('utf-8'), textof(real).encode('utf-8')))
        del sharon.chain._tweetstore[x.id]
        sharon.chain._tweetstore.add(real)
        replaced += 1
    except Exception as e:
      print('Error fetching @{}: {}    {}'.format(x.user.screen_name.encode('utf-8'), x.text.encode('utf-8'), str(e)))
      errors += 1
    time.sleep(1)
  print ('Processed {}, replacing {} with {} errors'.format(processed, replaced, errors))

