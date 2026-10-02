"""Read-only bounded reachability checks for public upstream file routes."""
from concurrent.futures import ThreadPoolExecutor
import json
import urllib.request

urls=['https://api.github.com/repos/GenEugene/GETools/commits/master',
      'https://raw.githubusercontent.com/GenEugene/GETools/master/LICENSE',
      'https://data.jsdelivr.com/v1/package/gh/GenEugene/GETools@master',
      'https://cdn.jsdelivr.net/gh/GenEugene/GETools@master/LICENSE']
def read(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'source-review'}),timeout=12) as response:
            data=response.read(4*1024*1024)
        if '/commits/' in url:
            print(json.dumps({'url':url,'sha':json.loads(data)['sha']}),flush=True)
        else:print(json.dumps({'url':url,'bytes':len(data),'prefix':data[:40].decode('utf-8','replace')}),flush=True)
    except Exception as error:print(json.dumps({'url':url,'error':str(error)}),flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(read,urls))
