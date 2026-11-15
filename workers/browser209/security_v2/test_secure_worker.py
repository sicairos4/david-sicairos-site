import asyncio, hashlib, importlib.util, json, socket, subprocess, unittest
from pathlib import Path
from unittest.mock import patch
s=importlib.util.spec_from_file_location('w',Path(__file__).with_name('secure_worker.py'))
w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
def job():
 t='{"steps": [{"action": "goto", "url": "https://example.com"}]}'
 return dict(id='job',claim_token='token',claim_generation=1,payload_text=t,payload=json.loads(t),payload_sha256=hashlib.sha256(t.encode()).hexdigest())
class Integrity(unittest.TestCase):
 def test_valid(self):self.assertEqual(w.payload(job()),job()['payload'])
 def test_tamper(self):
  j=job();j['payload_text']+=' '
  with self.assertRaises(ValueError):w.payload(j)
 def test_object(self):
  j=job();j['payload']={}
  with self.assertRaises(ValueError):w.payload(j)
 def test_size(self):
  j=job();j['payload_text']='x'*262145
  with self.assertRaises(ValueError):w.payload(j)
 def test_tls(self):
  for u in ('postgresql://u@db/d','http://db/d?sslmode=verify-full','postgresql://u@db/d?sslmode=verify-full&sslmode=disable','postgresql://u@db/d?sslmode=verify-full&options=x','postgresql://u@db/d?sslmode=verify-full&service=x'):
   with self.subTest(url=u),self.assertRaises(ValueError):w.connection_url(u)
 def test_tls_valid(self):self.assertIn('verify-full',w.connection_url('postgresql://u@db/d?sslmode=verify-full'))
class Runs(unittest.IsolatedAsyncioTestCase):
 async def test_success(self):
  calls=[]
  async def execute(j,beat):await beat()
  r=await w.run(job(),lambda *a:calls.append(a),execute)
  self.assertEqual(r['state'],'executed_unverified');self.assertEqual(calls[-1][0],'complete')
 async def test_failure(self):
  async def execute(*a):raise ValueError('mock')
  self.assertEqual((await w.run(job(),lambda *a:None,execute))['state'],'uncertain')
 async def test_denial(self):
  def call(op,p):
   if op=='heartbeat':raise ValueError('denied')
  async def execute(*a):self.fail('must not execute')
  self.assertEqual((await w.run(job(),call,execute))['state'],'uncertain')
 async def test_no_replay(self):
  def call(op,p):
   if op=='complete':raise ValueError('db')
  async def execute(*a):pass
  r=await w.run(job(),call,execute);self.assertEqual(r['state'],'completion_unrecorded');self.assertFalse(r['automatic_retry_allowed'])
 async def test_tamper_blocks_executor(self):
  j=job();j['payload_text']+=' '
  async def execute(*a):self.fail('must not execute')
  self.assertEqual((await w.run(j,lambda *a:None,execute))['state'],'uncertain')
def deny(*a,**k):raise RuntimeError('isolated')
if __name__=='__main__':
 loops=[asyncio.new_event_loop() for _ in range(5)]
 Runs._setupAsyncioRunner=lambda self:setattr(self,'_asyncioRunner',asyncio.Runner(loop_factory=lambda:loops.pop()))
 with patch.object(socket,'socket',deny),patch.object(socket,'create_connection',deny),patch.object(socket,'getaddrinfo',deny),patch.object(subprocess,'Popen',deny):
  for f in (lambda:socket.socket(),lambda:socket.create_connection(('example.com',443)),lambda:socket.getaddrinfo('example.com',443),lambda:subprocess.Popen(['echo'])):
   try:f()
   except RuntimeError:pass
   else:raise AssertionError('isolation_not_active')
  unittest.main(verbosity=2)
