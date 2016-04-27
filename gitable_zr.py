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

token = ""

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

def dump2(u,commits):
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    for event in w:
        # print(w)
        print('0' + str(w[0]))
        print('1' + str(w[1]))
        # commit_msg = w['message']
        # # committer_name = w['committer']['name']
        # commit_sha = w['sha']
        # # commit_date = w['committer']['date']
        # print(commit_msg)
        # # print(committer_name)
        # print(commit_sha)
        # print(commit_date)
        # issue_id = event['issue']['number']
        # if not event.get('label'): continue
        # created_at = secs(event['created_at'])
        # action = event['event']
        # label_name = event['label']['name']
        # user = event['actor']['login']
        # milestone = event['issue']['milestone']
        # if milestone != None : milestone = milestone['title']
        # eventObj = L(when=created_at,
        #                          action = action,
        #                          what = label_name,
        #                          user = user,
        #                          milestone = milestone)
        # all_events = issues.get(issue_id)
        # if not all_events: all_events = []
        # all_events.append(eventObj)
        # issues[issue_id] = all_events
    return True

def dump1(u,issues):
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

import time
from datetime import datetime
def dump_contributor(u,issues):
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    i = 1
    res_contributor = []
    res_totalCommits = []
    res_time = []
    res_commits = []
    for contributor in w:
        #print('Contributor: '+ str(i))
        res_contributor.append(contributor['author']['id'])
        #print('Total Commits: ' + str(contributor['total']))
        res_totalCommits.append(contributor['total'])
        temp_commits = []
        for week in contributor['weeks']:
            if i == 1:
                res_time.append(time.strftime('%Y-%m-%d', time.localtime(week['w'])))
                #res_time.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(week['w'])))
            temp_commits.append(week['c'])
            #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(week['w']))+","+str(week['c']))
            #print('# of additions: ' + str(week['a']))
            #print('# of deletions: ' + str(week['d']))
            #print('# of commits: ' + str(week['c']))
        res_commits.append(temp_commits)
        i = i+1

    #print out info in format
    print("Contributor, " + ', '.join(map(str,res_contributor)))
    print("Total Commits, " + ', '.join(map(str,res_totalCommits)))

    total_commits = sum(res_totalCommits)
    total_commits = float(total_commits)
    percent_commits = []
    for temp in res_totalCommits:
        percent_commits.append(round(temp/total_commits,3))

    print("Commits Contribution, " + ', '.join(map(str,percent_commits)))
    for i in range(1,len(res_time)):
        print(res_time[i] + "," + ','.join(map(str,(map(list,zip(*res_commits))[i]))))
    #print(res_commits[0:4][0])
    print()
    return True

def dump_totalCommits(u):
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    res_totalCommits = []
    for contributor in w:
        res_totalCommits.append(contributor['total'])

    print(', '.join(map(str,res_totalCommits)))
    return True

def dump_milestone(u,group):
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    i = 1
    res_milestone = []
    #print ('Group: %s' % link)
    #print("group,milestone,state,open issues,closed issues,created time,updated time,closed time,due time")
    for milestone in w:
        res_milestone = []
        #print(milestone)
        #print('Contributor: '+ str(i))
        res_milestone.append(group)
        res_milestone.append(milestone['id'])
        #print('Total Commits: ' + str(contributor['total']))
        res_milestone.append(milestone['state'])
        res_milestone.append(milestone['open_issues'])
        res_milestone.append(milestone['closed_issues'])
        res_milestone.append(milestone['created_at'])
        res_milestone.append(milestone['updated_at'])
        res_milestone.append(milestone['closed_at'])
        #closeTime = time.mktime(datetime.strptime(milestone['closed_at'].encode(),'%Y-%m-%dT%H:%M:%SZ').timetuple())
        res_milestone.append(milestone['due_on'])
        #dueTime = time.mktime(datetime.strptime(milestone['due_on'].encode(),'%Y-%m-%dT%H:%M:%SZ').timetuple())

        #TODO: new feature
        #Close milestones three days after due time or Even not close


        #if !milestone['closed_at'] or ['closed_at']>milestone['due_on']:
        #    res_milestone.append("TRUE")
        #else:
        #    res_milestone.append("FALSE")
        #if milestone['open_issues']>0:
        #    res_milestone.append("TRUE")
        #else:
        #    res_milestone.append("FALSE")

        #i = i+1
        #print out info in format
        print(', '.join(map(str,res_milestone)))

    return True

def dump_test(u):
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    i = 1
    res_milestone = []
    for milestone in w:
        print(i)
        print(milestone)
        i = i+1
        #print out info in format
        print(', '.join(map(str,res_milestone)))
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
    #links_to_repo = ['/nikign/Git-Helper']
    links_to_repo = ['/Arjun-Code-Knight/csc510-se-project', '/ankitkumar93/csc510-se-project',
         '/azhe825/CSC510', '/jordy-jose/CSC_510_group_d', '/DharmendraVaghela/csc510-grp-e',
         '/moharnab123saikia/CSC510-group-f', '/cleebp/csc-510-group-g', '/nikign/Git-Helper', '/shivamgulati1991/CSC510-SE-group-i',
         '/arnabsaha1011/mypackse', '/alokrk/csc510groupk', '/sandz-in/csc510_group_l',
         '/nikraina/CSC510', '/gvivek19/CSC510-Team-N']
    for link in links_to_repo:
        page = 1
        issues = dict()

        #print ('Group: %s' % link)
        # while(True):
            # use for time  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1454632798.0))
        # address = 'https://api.github.com/%s/graphs/contributors' % (link)
        #address = 'https://api.github.com/repos%s/commits' % (link)
        #contributor_address = 'https://api.github.com/repos%s/stats/contributors' % (link)
        milestone_address = 'https://api.github.com/repos%s/milestones?state=all' % (link)
        #test_address = 'https://api.github.com/repos%s/issues?state=all&page=1&per_page=1000' % (link)

        #doNext = dump2(address, issues)
        #doNext = dump_contributor(contributor_address, issues)
        #dump_totalCommits(contributor_address)

        doNext = dump_milestone(milestone_address,link)
        #doNext = dump_test(test_address)
        #print(time.strftime('%Y-%m-%d', time.localtime(1454632798.0)))

            # print("page "+ str(page))
            # page += 1
            # if not doNext : break
        #info[link] = copy.deepcopy(issues)
        #for issue, events in issues.iteritems():
        #    print("ISSUE " + str(issue))
        #    for event in events: print(event.show())
        #    print('')
        # print(str(info[link]))
        time.sleep(5)

launchDump()
