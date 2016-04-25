#  gitabel
#  the world's smallest project management tool
#  reports relabelling times in github (time in seconds since epoch)
#  thanks to dr parnin
#  todo:
#    - ensure events sorted by time
#    - add issue id
#    - add person handle

"""
You will need to add your authorization token in the code.
Here is how you do it.

1) In terminal run the following command

curl -i -u <your_username> -d '{"scopes": ["repo", "user"], "note": "OpenSciences"}' https://api.github.com/authorizations

2) Enter ur password on prompt. You will get a JSON response. 
In that response there will be a key called "token" . 
Copy the value for that key and paste it on line marked "token" in the attached source code. 

3) Run the python file. 

         python gitable.py

"""
 
from __future__ import print_function
import urllib2
import json
import re,datetime
import sys
 
class L():
    "Anonymous container"
    def __init__(i,**fields) : 
        i.override(fields)
    def override(i,d): i.__dict__.update(d); return i
    def __repr__(i):
        d = i.__dict__
        name = i.__class__.__name__
        return name+'{'+' '.join([':%s %s' % (k,pretty(d[k])) 
                                         for k in i.show()])+ '}'
    def show(i):
        lst = [str(k)+" : "+str(v) for k,v in i.__dict__.iteritems() if v != None]
        return ',\t'.join(map(str,lst))

    
def secs(d0):
    d     = datetime.datetime(*map(int, re.split('[^\d]', d0)[:-1]))
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = d - epoch
    return delta.total_seconds()
from datetime import time, datetime
import dateutil.parser

dates = {}
prev_data = None
def dump_commits(u,commits):
    global dates, prev_data
    token = "fdc02bd8ccae8c5edd61d9e6274487db0490926c" # <===
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    for commit in w:
        commit_msg = commit['commit']['message']
        committer_name = commit['commit']['committer']['name']
        commit_sha = commit['sha']
        commit_date = commit['commit']['committer']['date']
        date = dateutil.parser.parse(commit_date)
        if date.month not in dates:
            dates[date.month] = {}
        if date.day not in dates[date.month]:
            dates[date.month][date.day] = ['%s/%s' %(date.month, date.day), 0]
        dates[date.month][date.day][1] += 1
    return True
    

def dump1(u,issues):
    token = "afe23738bd0f24f3b15e632f3473363bd5733e33" # <===
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    for event in w:
        issue_id = event['issue']['number']
        if not event.get('label'): continue
        created_at = secs(event['created_at'])
        action = event['event']
        label_name = event['label']['name']
        user = event['actor']['login']
        milestone = event['issue']['milestone']
        if milestone != None : milestone = milestone['title']
        eventObj = L(when=created_at,
                                 action = action,
                                 what = label_name,
                                 user = user,
                                 milestone = milestone)
        all_events = issues.get(issue_id)
        if not all_events: all_events = []
        all_events.append(eventObj)
        issues[issue_id] = all_events
    return True

def dump(u,issues):
    try:
        return dump1(u, issues)
    except Exception as e: 
        print(e)
        print("Contact TA")
        return False
import copy
def launchDump():
    info = {}
    global dates
    # links_to_repo = ['/nikign/Git-Helper']
    links_to_repo = ['/Arjun-Code-Knight/csc510-se-project', '/ankitkumar93/csc510-se-project',
        '/azhe825/CSC510', '/jordy-jose/CSC_510_group_d', '/DharmendraVaghela/csc510-grp-e',
        '/moharnab123saikia/CSC510-group-f', '/cleebp/csc-510-group-g', '/nikign/SE-16', '/shivamgulati1991/CSC510-SE-group-i',
        '/arnabsaha1011/mypackse', '/alokrk/csc510groupk', '/sandz-in/csc510_group_l',
        '/nikraina/CSC510', '/gvivek19/CSC510-Team-N'] 
        
    for link in links_to_repo:
        page = 1
        issues = dict()
        print ('link: %s' % link)
        dates = {}
        while(True):
            # use for time  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1454632798.0))
        # address = 'https://api.github.com/%s/graphs/contributors' % (link)
            address = 'https://api.github.com/repos%s/commits?page=%d' % (link, page)
            # address = 'https://api.github.com/repos%s/issues/events?page=%d' % (link, page)
            doNext = dump_commits(address, issues)
            # print(doNext)
            # print("page "+ str(page))
            page += 1
            if not doNext : break
        for k in dates.keys():
            # print(k)
            for kk in dates[k].keys():
                print('%s\t%d' %(dates[k][kk][0], dates[k][kk][1]))
        # info[link] = copy.deepcopy(issues)
        # for issue, events in issues.iteritems():
        #     print("ISSUE " + str(issue))
        #     for event in events: print(event.show())
        #     print('')
        # print(str(info[link]))
        
launchDump()


    
     
 
