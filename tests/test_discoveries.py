import unittest, importlib.util, tempfile, json
from pathlib import Path
spec=importlib.util.spec_from_file_location('discoveries',Path(__file__).resolve().parents[1]/'scripts/refresh_discoveries.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def product():
 return dict(id=1,title='Black distressed thermal',handle='thermal',body_html='<p>Layered waffle texture</p>',images=[{'src':'https://cdn.shopify.com/thermal.jpg'}],variants=[{'available':True}],published_at='2026-10-01')
class DiscoveryTests(unittest.TestCase):
 def test_transform(self):
  result=module.transform([product()],'jaded','Jaded London','https://jadedldn.com','2026-10-10')
  self.assertEqual(result[0]['sourceUrl'],'https://jadedldn.com/products/thermal');self.assertIn('distress',result[0]['tags']);self.assertIsNone(result[0]['price'])
 def test_out_of_stock_omitted(self):
  p=product();p['variants'][0]['available']=False;self.assertEqual(module.transform([p],'jaded','Jaded London','https://jadedldn.com','2026-10-10'),[])
 def test_store_failure_preserves_last_good_products(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'feed.json';old=module.refresh(path,lambda slug,base:[product()])
   def partial(slug,base):
    if slug=='affliction':raise OSError('offline')
    return [product()]
   new=module.refresh(path,partial);self.assertEqual(len(new['items']),3);self.assertEqual(new['sources'][1]['status'],'cached')
   contents=path.read_text()
   with self.assertRaises(RuntimeError): module.refresh(path,lambda *args: (_ for _ in ()).throw(OSError()))
   self.assertEqual(path.read_text(),contents)
