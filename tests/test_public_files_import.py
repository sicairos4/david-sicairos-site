import copy, importlib.util, pathlib, unittest
spec=importlib.util.spec_from_file_location('catalog',pathlib.Path(__file__).resolve().parents[1]/'scripts/import_public_files.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BASE={'schema_version':1,'documents':[{'title':'Test','description':'Test fixture only','agency':'Test agency','document_type':'Response','sha256':'a'*64,'retrieved_at':'2026-10-21T09:27:00-07:00','source_url':'https://example.org/source','public_document_url':'https://example.org/release','keywords':['CPRA'],'document_date':None}]}
class Validation(unittest.TestCase):
 def reject(self,key,value):
  d=copy.deepcopy(BASE);d['documents'][0][key]=value
  with self.assertRaises(ValueError):m.validate(d)
 def test_valid(self):self.assertEqual(len(m.validate(BASE)),1)
 def test_hash(self):self.reject('sha256','x')
 def test_url(self):self.reject('public_document_url','javascript:alert(1)')
 def test_credentials(self):self.reject('source_url','https://u:p@example.org')
 def test_timezone(self):self.reject('retrieved_at','2026-10-21T09:00:00')
 def test_tags(self):self.reject('keywords','bad')
 def test_duplicates(self):
  d=copy.deepcopy(BASE);d['documents']*=2
  with self.assertRaises(ValueError):m.validate(d)
 def test_draft_only(self):
  d=copy.deepcopy(BASE);d['documents'][0].update(review_status='published',redaction_reviewed=True)
  row=m.validate(d)[0];self.assertEqual(row['review_status'],'draft');self.assertFalse(row['redaction_reviewed'])
 def test_private_extras(self):
  d=copy.deepcopy(BASE);d['documents'][0]['gmail_message_id']='private'
  self.assertNotIn('gmail_message_id',m.validate(d)[0])
if __name__=='__main__':unittest.main()
