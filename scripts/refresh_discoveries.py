"""Refresh public product discoveries. No credentials or personal reference data."""
import json, re, html, urllib.request
from pathlib import Path
from datetime import datetime, timezone
SOURCES = [('jaded','Jaded London','https://jadedldn.com'), ('affliction','Affliction','https://www.afflictionclothing.com'), ('edhardy','Ed Hardy','https://edhardyoriginals.com')]
RULES = {'dark':r'black|charcoal|washed|oxblood|grey|gray','distress':r'distress|ripped|destroy|raw edge|washed','fitted':r'fitted|slim|corset|ribbed|baby tee','mesh':r'mesh|sheer|lace','denim':r'denim|jean','flare':r'flare|bootcut','graphic':r'graphic|print|skull|cross|tattoo|tee','knit':r'knit|waffle|thermal|ribbed','layer':r'layer|henley|thermal','silver':r'silver|hardware|stud|rhinestone|chain|zip'}
def transform(products, slug, brand, base, observed):
    out=[]
    for p in products:
        title=str(p.get('title','')).strip()
        description=html.unescape(re.sub('<[^>]+>',' ',p.get('body_html') or ''))
        text=(title+' '+description+' '+str(p.get('product_type',''))).lower()
        if re.search(r'\bwomen|\bwomens|\bfemale', ' '.join(p.get('tags',[])).lower()): continue
        if not title or not p.get('handle') or not p.get('images') or not any(v.get('available') for v in p.get('variants',[])): continue
        if re.search(r'scorpion|moth|checkered|chinese dragon',text): continue
        tags=[k for k,v in RULES.items() if re.search(v,text)]
        if not tags: continue
        category='Denim' if 'denim' in tags else 'Bottoms' if re.search(r'pant|short|skirt|jogger',text) else 'Outerwear' if re.search(r'jacket|hoodie|cardigan|coat',title.lower()) else 'Tops'
        image=p['images'][0].get('src','')
        if not image.startswith('https://'): continue
        out.append(dict(id=f'store-{slug}-{p["id"]}',title=title,brand=brand,category=category,categories=[category],sourceUrl=base+'/products/'+p['handle'],sourceLabel=brand+' · official store',observedAt=observed,sourceFacts=description.strip()[:1500] or 'Product listed by the official store. Check the store for current availability, sizing and price.',tags=tags,price=None,kind='product',imageKey='',imageUrl=image,origin='discovery',publishedAt=p.get('published_at'),originalSha256='',revision=1,influence=1))
    # Keep a mix of brands, newest listings first, favor textured/dark shapes.
    return sorted(out,key=lambda p:(p.get('publishedAt') or '',len(p['tags'])),reverse=True)[:100]
def refresh(path, fetch=None):
    observed=datetime.now(timezone.utc).isoformat()
    old=json.loads(path.read_text()) if path.exists() else {'items':[],'sources':[]}
    items=[]; health=[]; success=0
    for slug,brand,base in SOURCES:
        try:
            if fetch: products=fetch(slug,base)
            else:
                req=urllib.request.Request(base+'/products.json?limit=250',headers={'User-Agent':'Oblivyx-Discovery/1.0'})
                with urllib.request.urlopen(req,timeout=40) as response: products=json.load(response)['products']
            current=transform(products,slug,brand,base,observed)
            if not current: raise ValueError('No usable products')
            success+=1
            health.append(dict(brand=brand,status='ok',checkedAt=observed,count=len(current)))
        except Exception:
            current=[p for p in old['items'] if p.get('brand')==brand]
            previous=next((s for s in old.get('sources',[]) if s['brand']==brand),{})
            health.append(dict(brand=brand,status='cached',checkedAt=previous.get('checkedAt'),count=len(current)))
        items.extend(current)
    if not success: raise RuntimeError('All stores failed; existing feed left unchanged')
    feed=dict(schemaVersion=1,checkedAt=observed,sources=health,items=items)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(feed,ensure_ascii=False,indent=2)+'\n')
    return feed
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--fixtures',type=Path); args=parser.parse_args()
    fetch=(lambda slug,base: json.loads((args.fixtures/(slug+'-products.json')).read_text())['products']) if args.fixtures else None
    feed=refresh(Path(__file__).resolve().parents[1]/'feeds/sample-size.json',fetch)
    print(f'{len(feed["items"])} products; '+', '.join(s['brand']+': '+s['status'] for s in feed['sources']))
