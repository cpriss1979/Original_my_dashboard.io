import http.server, json, urllib.request, urllib.parse, urllib.error, pathlib, threading, webbrowser
ROOT=pathlib.Path(__file__).resolve().parent
KEY=''
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(ROOT),**kw)
 def log_message(self,*args):pass
 def reply(self,status,data):
  body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def valid_host(self):return self.headers.get('Host') in ['127.0.0.1:8765','localhost:8765']
 def do_POST(self):
  global KEY
  if not self.valid_host() or self.headers.get('Origin') not in ['http://127.0.0.1:8765','http://localhost:8765']:return self.reply(403,{'error':'Local dashboard requests only.'})
  if self.path!='/api/esv-key':return self.reply(404,{'error':'Not found'})
  try:
   n=int(self.headers.get('Content-Length',0))
   if not 0<n<=4096:raise ValueError()
   key=json.loads(self.rfile.read(n)).get('key','')
   if not isinstance(key,str) or not key or len(key)>1000 or '\n' in key or '\r' in key:raise ValueError()
   KEY=key;self.reply(200,{'ok':True})
  except Exception:self.reply(400,{'error':'Enter a valid ESV API key.'})
 def do_GET(self):
  if not self.valid_host():return self.reply(403,{'error':'Local dashboard requests only.'})
  path=urllib.parse.urlparse(self.path)
  if path.path!='/api/esv':return super().do_GET()
  if not KEY:return self.reply(401,{'error':'Open Bible → Connect ESV privately and enter your API key.'})
  ref=urllib.parse.parse_qs(path.query).get('q',[''])[0]
  if not ref or len(ref)>150:return self.reply(400,{'error':'Enter a Bible reference.'})
  query=urllib.parse.urlencode({'q':ref,'include-footnotes':'false','include-short-copyright':'true','include-passage-references':'true'})
  req=urllib.request.Request('https://api.esv.org/v3/passage/text/?'+query,headers={'Authorization':'Token '+KEY})
  try:
   with urllib.request.urlopen(req,timeout=20) as r:data=json.load(r)
   if not data.get('passages'):return self.reply(404,{'error':'No passage found. Check your book, chapter and verse.'})
   self.reply(200,data)
  except urllib.error.HTTPError as e:self.reply(502,{'error':'ESV request failed ('+str(e.code)+'). Check your key, passage, or service limits.'})
  except Exception:self.reply(502,{'error':'Unable to reach ESV. Check your internet connection.'})
if __name__=='__main__':
 try:server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),Handler)
 except OSError:raise SystemExit('Port 8765 is already in use. Stop your previous dashboard server, then try again.')
 print('Dashboard: http://127.0.0.1:8765/index.html\nKeep this window open. Control-C stops the server and clears your ESV key.')
 threading.Timer(1,lambda:webbrowser.open('http://127.0.0.1:8765/index.html')).start()
 try:server.serve_forever()
 except KeyboardInterrupt:server.server_close();KEY=''
