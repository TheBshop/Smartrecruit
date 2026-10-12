import json,re
def tables(v):
    tabs=v.get('t') or v.get('tabs') or []
    out=[]
    for t in tabs:
        if isinstance(t,dict): out.append([t['h']]+t['rows'])
        else: out.append(t)
    return out
def find(v):
    for t in tables(v):
        if not t: continue
        h=[x.lower() for x in t[0]]
        if 'player' in h and 'gp' in h and ('pts' in h or 'g' in h): return h,t[1:]
    return None
if __name__=='__main__':
    d=json.load(open('all.json'))
    bad=[];ok=[]
    for team,v in d.items():
        r=find(v)
        if not r: bad.append((team,v['url'][:70],len(tables(v))));continue
        ok.append((team,r[0],len(r[1]),v['url']))
    print(len(ok),'ok',len(bad),'bad');print(bad)
    hs={}
    for t,h,n,u in ok: hs.setdefault(tuple(h),[]).append(t)
    for h,ts in hs.items(): print(h,len(ts),ts[:3])
