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

def count_in_week(openTime, time_list):
    global weekTime
    for i in xrange(len(time_list)):
        if weekTime[i] <= openTime <= weekTime[i+1]:
            time_list[i] += 1
            break


def def_weeks():
    global commentsOpenPerWeek, commitsOpenPerWeek, weekTime
    projectStart = datetime.strptime('2016-01-09T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
    weekTime = [projectStart]
    for i in xrange(1,14):
        weekTime.append(weekTime[i-1]+ timedelta(days =7))
    commitsOpenPerWeek = [0]*13
    commentsOpenPerWeek = [0]*13

def secs(d0):
    d     = datetime.datetime(*map(int, re.split('[^\d]', d0)[:-1]))
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = d - epoch
    return delta.total_seconds()
from datetime import time, datetime, timedelta
import dateutil.parser

prev_data = None
name_id_map = {}
def dump_commits(u):
    global dates, prev_data, users, commitsOpenPerWeek
    token = "1368f9fb884de63474ff11fbe80457f93f210962" # <===
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    for commit in w:
        if commit['author'] is None:
            if 'None' not in users:
                users['None'] = 0
            users['None'] += 1
            continue  
        committer_id = commit['author']['id']
        commit_date = commit['commit']['committer']['date']
        date = dateutil.parser.parse(commit_date)
        naive = date.replace(tzinfo=None)
        count_in_week(naive, commitsOpenPerWeek)
        if committer_id not in users:
            continue
        users[committer_id] += 1

    return True

users = {}
def dump_comments(u):
    global dates, prev_data, users, commentsOpenPerWeek
    token = "1368f9fb884de63474ff11fbe80457f93f210962" # <===
    request = urllib2.Request(u, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    for comment in w:
        user = comment['user']['id']
        if user not in users:
            continue

        print( comment.keys())
        date = comment['created_at']
        date = dateutil.parser.parse(date)
        naive = date.replace(tzinfo=None)
        count_in_week(naive, commentsOpenPerWeek)
        users[user] += 1
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
def dumpCommits():

    info = {}

    global dates, users, links_to_repo, commitsOpenPerWeek
        
    groups = {}
    with open("commit_out.txt", 'w') as out:
        for link in links_to_repo:
            def_weeks()
            page = 1
            users = {}
            fill_group_users(link)
            while(True):
                address = 'https://api.github.com/repos%s/commits?page=%d' % (link, page)
                doNext = dump_commits(address)
                page += 1
                if not doNext : break
            out.write('%s\t%s\n' %(link, str(commitsOpenPerWeek)))

        for user in users.keys():
            print('%s\t%d' %(user, users[user]))

        mean = numpy.mean(users.values())
        sdev = numpy.std(users.values())

        scores = [(user - mean)/(1.0*sdev) for user in users.values() if user is not 'None']
        bad_smell = 0
        for score in scores:
            if score < -1.5 or score > 1.5:
                bad_smell = 1
                break
        if bad_smell:
            print('Group %s has bad smell' % link)
        group_count = len(users.values()) if 'None' not in users.keys() else len(users.values())-1
        none_count = users['None'] if 'None' in users else 0
        groups[link] = (bad_smell, sum(users.values())*1.0/group_count, none_count)
    find_outlier_groups(groups)
    max_sum = max([group[1] for group in groups.values()])
    print("group name\toutlier in group commits\ttotal commits\tNone Author commits")
    for link in groups:
        bad_smell2 = 1 - (groups[link][1]*1.0)/max_sum
        print("%s\t%f\t%f\t%d" %(link, groups[link][0], bad_smell2, groups[link][2]))
    

import numpy
def find_outlier_groups(groups):

    # groups_sdev = [i[0] for i in groups.values()]
    groups_sum = [i[1] for i in groups.values()]

    sum_sdev = numpy.std(numpy.array(groups_sum))
    sum_mean = numpy.mean(numpy.array(groups_sum))

    # total_sdev = numpy.std(numpy.array(groups_sdev))
    # total_mean = numpy.mean(numpy.array(groups_sdev))
    for group in groups.keys():
        group_sum_score = (groups[group][1] - sum_mean)/(1.0*sum_sdev)
        # group_sdev_score = (groups[group][0] - total_mean)/(1.0*total_sdev)
        # print('group: %s, sdev score: %f, sum score: %f' %(group, group_sdev_score, group_sum_score))
        # if group_sdev_score > 1.5 or group_sdev_score < -1.5:
        #     print('Group with much sdev: %s' %group)
        if group_sum_score < -1.5:
            print('Group with low comments: %s' %group)

total_users = {}
def fill_group_users(link):
    global users, total_users
    address = 'https://api.github.com/repos%s/stats/contributors' % link
    token = "1368f9fb884de63474ff11fbe80457f93f210962" # <===
    request = urllib2.Request(address, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    if not w: return False
    user_ids = [ww['author']['id'] for ww in w]
    user_keys = [(ww['author']['id'], ww['author']['login']) for ww in w]
    total_users[link] = user_ids
    for user_id in user_ids:
        users[user_id] = 0
    
            
issues = {}
def count_issues():
    global issues, links_to_repo

    for link in links_to_repo:
        issue_address = 'https://api.github.com/repos%s/issues?state=all&page=1&per_page=1000' % (link)
        token = "1368f9fb884de63474ff11fbe80457f93f210962" # <===
        request = urllib2.Request(issue_address, headers={"Authorization" : "token "+token})
        v = urllib2.urlopen(request).read()
        w = json.loads(v)
        issues[link] = len(w)
    print(str(issues))
    


links_to_repo = ['/Arjun-Code-Knight/csc510-se-project', '/ankitkumar93/csc510-se-project',
    '/azhe825/CSC510', '/jordy-jose/CSC_510_group_d', '/DharmendraVaghela/csc510-grp-e',
    '/moharnab123saikia/CSC510-group-f', '/cleebp/csc-510-group-g', '/nikign/SE-16', '/shivamgulati1991/CSC510-SE-group-i',
    '/arnabsaha1011/mypackse', '/alokrk/csc510groupk', '/sandz-in/csc510_group_l',
    '/nikraina/CSC510', '/gvivek19/CSC510-Team-N'] 
def dumpComments():
    info = {}
    global dates, users, links_to_repo, issues, commentsOpenPerWeek
    count_issues()
    groups = {}

    with open("comment_out.txt", 'w') as out:
        for link in links_to_repo:
            page = 1
            users = {}
            fill_group_users(link)
            def_weeks()
            while(True):
                address = 'https://api.github.com/repos%s/issues/comments?page=%d' % (link, page)
                doNext = dump_comments(address)
                # print('page: %d' % page)
                page += 1
                if not doNext : break
            out.write('%s\t%s\n' %(link, str(commentsOpenPerWeek)))
        print ('link: %s' % link)
        for user in users.keys():
            print('%s\t%d' %(user, users[user]))

        mean = numpy.mean(users.values())
        sdev = numpy.std(users.values())

        scores = [(user - mean)/(1.0*sdev) for user in users.values() if user is not 'None']
        bad_smell = 0
        for score in scores:
            if score < -1.5 or score > 1.5:
                bad_smell = 1
                break
        print(str(issues.keys()))
        issue_count = issues[link]
        group_count = len(users.values()) if 'None' not in users.keys() else len(users.values())-1
        none_count = users['None'] if 'None' in users else 0
        groups[link] = (bad_smell, sum(users.values())*1.0/(issue_count*group_count))
    find_outlier_groups(groups)
    max_sum = max([group[1] for group in groups.values()])
    print("group name\toutlier in group comments\ttotal comments")
    for link in groups:
        bad_smell2 = 1 - (groups[link][1]*1.0)/max_sum
        print("%s\t%f\t%f" %(link, groups[link][0], bad_smell2))

    
dumpComments()
# dumpCommits()


    
     
 
