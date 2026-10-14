#!/bin/zsh
cd -- "${0:A:h}"
python3 - <<'PYCODE'
import http.server, functools, threading, webbrowser
handler=functools.partial(http.server.SimpleHTTPRequestHandler, directory='.')
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),handler)
url='http://127.0.0.1:'+str(server.server_port)+'/index.html'
print('Dashboard is running at '+url+'\nKeep this window open while using it. Press Control-C to stop.')
threading.Timer(1,lambda:webbrowser.open(url)).start()
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
PYCODE
