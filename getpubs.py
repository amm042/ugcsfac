"""
Create a list of pubs and metadata from DBLP using their web api
https://dblp.org/faq/13501473.html
Alan Marchiori 2019

https://www.bucknell.edu/azdirectory/institutional-research-planning/peer-group-institutions

"""

import requests as req
import csv
import os
from pprint import pprint
import threading
import queue

def getauthor(authorName, url="https://dblp.org/search/author/api"):
    "Does an author query to return all variations of an author's name"
    authorName = " ".join([x+"$" for x in authorName.split()])
    print("Searching author {}".format(authorName))
    r = req.get(url,
                params = {
                    "q":authorName,
                    "format":"json"
                    })
    q = r.json()
    if 'result' in q and 'hit' in q['result']['hits']:
        return [hit['info']['author'] for hit in q['result']['hits']['hit']]
    else:
        return []
def getpubs(author, url="http://dblp.org/search/publ/api"):
    "get pubs from an author, does not support more than 1000 results."
    print("Getting pubs from {}".format(author))
    r = req.get(url,
                params = {
                    "q":author,
                    "format":"json",
                    "h": 1000
                    })
    q = r.json()
    r = []
    if 'result' in q:
        for hit in q['result']['hits']['hit']:
            if author in hit['info']['authors']['author']:
                # smash list of authors
                if isinstance(hit['info']['authors']['author'], list):
                    hit['info']['authors'] = ", ".join(hit['info']['authors']['author'])
                else:
                    hit['info']['authors'] = hit['info']['authors']['author']
                r.append(hit['info'])
    else:
        print("ERR: "+r.text)

    return r

def getallpubs(q, uname, facname):
    for authorname in getauthor(facname):
        try:
            pubs = getpubs(authorname)

            for p in pubs:
                p['university'] = uname
                q.put(p)
        except Exception as x:
            print('ERR' + str(x))
            pass
if __name__=="__main__":
    pubq = queue.Queue()

    ts = []
    allpubs = []
    cols = set()
    done = []

    if os.path.exists('status'):
        with open('status', 'r') as f:
            done = f.read().split()

    for facfile in os.listdir('faculty'):
        uname = os.path.splitext(facfile)[0]

        if uname in done:
            print("skipping {}".format(uname))
            continue

        with open(os.path.join('faculty', facfile), "r") as f:
            faculty = f.read().split('\n')

        for facname in faculty:
            t = threading.Thread(target=getallpubs,
                                 args=(pubq, uname, facname),
                                 name="{}/{}".format(uname, facname))
            t.start()
            ts.append(t)

        with open('status', 'a') as f:
            print(uname, file=f)

    for t in ts:
        print("Waiting on {}".format(t.name))
        t.join()

    # collect the data.
    while not pubq.empty():
        p = pubq.get()
        allpubs.append(p)



    if os.path.exists('pubs.csv'):
        #read and append!
        with open('pubs.csv', 'r') as f:
            dr = csv.DictReader(f)
            for row in dr:
                allpubs.append(row)

    # build column set
    for p in allpubs:
        for k in p.keys():
            if k not in cols:
                cols.add(k)

    cols = sorted(list(cols))

    with open('pubs.csv', 'w') as f:
        w = csv.DictWriter(f, fieldnames = cols)
        w.writeheader()
        for p in allpubs:
            w.writerow(p)
