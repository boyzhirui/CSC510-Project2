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
import re
import sys
import pprint
import copy, time, datetime, numpy, pickle


 

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

def dump1(u,issues):
    token = "6859f2aee01021d1383da05444e3e9eb15597e98" # <===
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

def zcoreCal(input):
    input = numpy.array(input)
    inputMean = numpy.mean(input)
    inputStd = numpy.std(input)
    inputZcore = numpy.array([round((t - inputMean)/inputStd,4) for t in input])
    inputAbnormalCounts = numpy.compress((inputZcore<-1.5) | (inputZcore>1.5),inputZcore).size
    return inputAbnormalCounts


def dumpLables(address):
    token = "6859f2aee01021d1383da05444e3e9eb15597e98" # <===
    request = urllib2.Request(address, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    print (len(w))
    pprint.pprint (w)
    labelList = []
    for label in w:
        if label['name'] not in ['bug', 'duplicate', 'enhancement', 'help wanted', 'invalid', 'question', 'wontfix']:
            labelList.append(label['name'])

    return labelList


def dumpIssues( groupIndex,groupname, address, labelList, groupIDs):
    token = "6859f2aee01021d1383da05444e3e9eb15597e98" # <===
    request = urllib2.Request(address, headers={"Authorization" : "token "+token})
    v = urllib2.urlopen(request).read()
    w = json.loads(v)
    contributor_dic = {}
    labels_counts_dic = {}
    labels_times_dic ={}
    openIssueCounts = 0
    closedIssueCounts = 0
    commentsCounts = 0
    unlabeledMilestoneIssue =0
    uncommentedIssue = 0
    unusedLableCount = 0
    unlabeledLabelIssue = 0
    issuesClosedAfterMilestone = 0
    issuesLastTime = []
    issuesLableCounts =[]

    projectStart = datetime.datetime.strptime('2016-01-09T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
    weekTime = [projectStart]
    for i in xrange(1,14):
        weekTime.append(weekTime[i-1]+ datetime.timedelta(days =7))
    issuesOpenPerWeek = [0]*13
    issuesClosedPerWeek = [0]*13
    # print("=============================================================")
    # print (groupname)
    if not w: return False
    for issue in w:
        #print("=============================================================")
        # pprint.pprint(issue)
        if issue['assignee'] !=None:
            if issue['assignee']['login'] not in ['timm', "shaowns"]:

                if issue['assignee']['id'] not in contributor_dic.keys():
                    contributor_dic[issue['assignee']['id']] = 1
                else:
                    contributor_dic[issue['assignee']['id']] += 1

        if groupname == '/nikraina/CSC510': contributor_dic['14355734'] = 0

        if issue['state'] == 'open':
            openIssueCounts +=1
            issueLastTime = float("inf")
            closeTime = None

        else:
            closedIssueCounts +=1
            closeTime = datetime.datetime.strptime(issue['closed_at'].encode(),\
                                                      '%Y-%m-%dT%H:%M:%SZ')
            openTime = datetime.datetime.strptime(issue['created_at'].encode(),\
                                                     '%Y-%m-%dT%H:%M:%SZ')
            #issueLastTime = time.mktime(closeTime.timetuple()) - time.mktime(openTime.timetuple())
            # issue last time in hour
            issueLastTime = round( (closeTime - openTime).total_seconds()/3600,4)
            issuesLastTime.append(issueLastTime)
            # Number of issues open per week
            for i in xrange(len(issuesOpenPerWeek)):
                #print(openTime)
                if weekTime[i] <= openTime <= weekTime[i+1]:
                    issuesOpenPerWeek[i] += 1
                    break
            for i in xrange(len(issuesOpenPerWeek)):
                if weekTime[i] <= closeTime <=weekTime[i+1]:
                    issuesClosedPerWeek[i] +=1
                    break



        if issue['labels'] != []:
            issuesLableCounts.append(len(issue['labels']))
            for label in issue['labels']:
                if label['name'] not in labels_counts_dic.keys():
                    labels_counts_dic[label['name']]= 1
                    labels_times_dic[label['name']] = [issueLastTime]
                else:
                    labels_counts_dic[label['name']] +=1
                    labels_times_dic[label['name']].append(issueLastTime)
        else: 
            unlabeledLabelIssue +=1


        if issue['milestone'] == None:
            unlabeledMilestoneIssue += 1

        else:
            if issue['milestone']['due_on'] != None:
                milestoneDueTime = datetime.datetime.strptime(issue['milestone']['due_on'].encode(),\
                                                      '%Y-%m-%dT%H:%M:%SZ')
                if closeTime == None or closeTime>milestoneDueTime:
                    issuesClosedAfterMilestone += 1


        if issue['comments'] == 0: uncommentedIssue += 1
        commentsCounts += issue['comments']
    # assignee
    assignedIssueByPerson = contributor_dic.values()
    assignedIssue = sum(assignedIssueByPerson)
    assignedIssueAbnormal = zcoreCal(assignedIssueByPerson)
    totalIssue = openIssueCounts+closedIssueCounts
    totalLabels = len(labels_counts_dic.keys())
    # print (groupIDs)
    # print (contributor_dic.keys())



    # Caculation issue time
    issueTimeAbnormal = zcoreCal(issuesLastTime)
    issuesOpenAbnormal = zcoreCal(issuesOpenPerWeek)
    issuesClosedAbnormal = zcoreCal(issuesClosedPerWeek)

    # caculation for issue label
    #issuesLableCounts = numpy.array(issuesLableCounts)
    #issuesLabelMean = numpy.mean(issuesLableCounts)
    #issuesLabelStd = numpy.std(issuesLableCounts)
    #issuesLabelZcore = numpy.array([round((l-issuesLabelMean)/issuesLabelStd,4) for l in issuesLableCounts])
    #issuesLabelNormal = numpy.compress((issuesLabelZcore>=-2) & (issuesLabelZcore<=2), issuesLabelZcore).size

    for l in labelList:
        if l not in labels_times_dic.keys():
            unusedLableCount +=1
            print ("used label name %s" % l)
    print (unusedLableCount)
    groupfile = open("Group"+str(groupIndex) + "-IssuesInfo.txt", "a")
    groupfile.write ("Groupname: %s \n\n" % groupname)
    groupfile.write("============================================================= \n")
    groupfile.write("=======================Assignee================================\n")
    groupfile.write("=============================================================\n")

    groupfile.write ('Uneven contribution on assigning issues,')
    groupfile.write ( str(assignedIssueAbnormal))
    groupfile.write ('\n')
    groupfile.write ("Number of issues assigned to each person,")
    groupfile.write (str(contributor_dic))
    groupfile.write ('\n\n')

    groupfile.write("=============================================================\n")
    groupfile.write("=======================ISSUES================================\n")
    groupfile.write("=============================================================\n")
    groupfile.write ("Total number of issues,%d \n" % (totalIssue))
    groupfile.write ("Issues last time,")
    groupfile.write (str(issuesLastTime))
    groupfile.write ('\n')
    groupfile.write ("Issues opened per week,")
    groupfile.write (str(issuesOpenPerWeek))
    groupfile.write ("\n")
    groupfile.write ("Issues closed per week,")
    groupfile.write (str(issuesClosedPerWeek))
    groupfile.write ("\n")
    groupfile.write ("Unusual weekly activity of open too many issues or none issue," )
    groupfile.write ( str( issuesOpenAbnormal))
    groupfile.write ('\n')
    groupfile.write ("Unusual weekly activity of close too many issues or none issue,")
    groupfile.write (str(issuesClosedAbnormal))
    groupfile.write ('\n')
    groupfile.write ("Issues lasting time mean, %.2f\n", issuesTimeMean)
    groupfile.write ("Issues lasting time std, %.2f\n", issuesTimeStd)
    groupfile.write ("Issues lasting time zscore, %.2f \n", issuesLabelZcore)
    groupfile.write ("Number and percentage of Issues with unusually long or short  lasting time, %d , %.0f%% \n" % \
           (issueTimeAbnormal, 100*issueTimeAbnormal/totalIssue))
    #print ("Issues with abnormal label counts, %d, %.0f%% \n " % \
    #       ((totalIssue -issuesLabelNormal), 100*(totalIssue-issuesLabelNormal)/totalIssue))
    #print ("Unclosed issues,%d\n" % openIssueCounts)
    #print ("unclosed isseus percentage," , float(openIssueCounts)/float(totalIssue))
    groupfile.write ("Number of unclosed issues after April 9, %d \n" % (totalIssue - sum(issuesClosedPerWeek)))
    groupfile.write ('Number and percentage of issues closed after milestone deadline, %d \n' % issuesClosedAfterMilestone)

    groupfile.write ("Number and Percentage of issues without comments, %d, %.0f%% \n " % (uncommentedIssue, 100*uncommentedIssue/totalIssue))
    groupfile.write ("Number and Percentage of issues without milestone label, %d, %.0f%% \n" % (unlabeledMilestoneIssue, 100*unlabeledMilestoneIssue/totalIssue))
    groupfile.write ("Number and Percentage of issues without any label, %d, %.0f%% \n" % (unlabeledLabelIssue, 100*unlabeledLabelIssue/totalIssue))
    groupfile.write ("Number and Percentage of issues without assignee, %d, %.0f%% \n" % ((totalIssue-assignedIssue), 100* (totalIssue-assignedIssue)/totalIssue))
    groupfile.write ('\n\n')
    groupfile.write("=============================================================\n")
    groupfile.write("=======================Labels================================\n")
    groupfile.write("=============================================================\n")
    groupfile.write ("Total labels, %d \n" % totalLabels)
    groupfile.write ("Amount of time each label lasting, ")
    groupfile.write ( str(labels_times_dic))
    groupfile.write ('\n')
    groupfile.write ("Number of counts each label were used,")
    groupfile.write ( str(labels_counts_dic))
    groupfile.write ('\n')
    groupfile.write ("Number of unused labels counts, %d " % unusedLableCount)

    groupfile.close()



    BadSmellFiles.write(','.join([groupname,\

        # Uneven contribution on assigning issues
        calScore(assignedIssueAbnormal),\

        # Unusual activity of open  issues
        calScore(issuesOpenAbnormal),\

        #Number of weeks has unusually open issues activity
        str(issuesOpenAbnormal),\

        # Unusual activity of close issue
        calScore(issuesClosedAbnormal),\

        #Number of weeks has unusually close issues activity
        str(issuesClosedAbnormal),\

        # percentage of Issues with unusually long or short lasting time,
        str(float(issueTimeAbnormal)/float(totalIssue)),\

        # Unclosed issues after April 9,
        calScore(totalIssue - sum(issuesClosedPerWeek)),\

        # issues closed after milestone deadline,
        str(float(issuesClosedAfterMilestone)/float(totalIssue)), \

        # Percentage of issues without comments, 
        str(float(uncommentedIssue)/float(totalIssue)),\

        #Percentage of issues without milestone label,
        str(float(unlabeledMilestoneIssue)/float(totalIssue)),\

        #Percentage of issues without any label
        str(float(unlabeledLabelIssue)/float(totalIssue)),\

        # Percentage of issues without assignee,
        str(float(totalIssue-assignedIssue)/float(totalIssue)),\

        # Number of unused labels counts
        calScore(unusedLableCount),\

        # total number of issues
        str(totalIssue),\

        # total number of labels
        str(totalLabels), '\n']))

    return True

def calScore(grade):
    if grade >0:
        return str(1)
    else:
        return str(0)

def dump(u,issues):
    try:
        return dump1(u, issues)
    except Exception as e: 
        print(e)
        print("Contact TA")
        return False



def launchDump():
    info = {}

    links_to_repo = ['/Arjun-Code-Knight/csc510-se-project', '/ankitkumar93/csc510-se-project',
                     '/azhe825/CSC510', '/jordy-jose/CSC_510_group_d', '/DharmendraVaghela/csc510-grp-e',
                     '/moharnab123saikia/CSC510-group-f', '/cleebp/csc-510-group-g', '/nikign/Git-Helper',
                     '/shivamgulati1991/CSC510-SE-group-i',
                     '/arnabsaha1011/mypackse', '/alokrk/csc510groupk', '/sandz-in/csc510_group_l',
                     '/nikraina/CSC510', '/gvivek19/CSC510-Team-N']

    #links_to_repo = ['/nikign/Git-Helper']
    #links_to_repo = ['/gvivek19/CSC510-Team-N']

    f = open("LablesLists", "r")
    labelLists = pickle.load(f)
    f.close()

    #load group IDs Dictionary
    f =  open("user_ids.json", "r")
    groupIDdic = eval(f.read())
    f.close()
    #print (groupIDdic.keys())
    # print (type(groupIDdic))

    for groupname in links_to_repo:
        print (groupname)
        time.sleep(5)
        issues = dict()
        print ('Group Name: %s' % groupname)
        #address_labels = "https://api.github.com/repos%s/labels" % (link)
        address_issues = 'https://api.github.com/repos%s/issues?state=all&page=1&per_page=100' % (groupname)

        #address_labels = 'https://api.github.com/repos/lintingting/Testing/labels'
        #address_issues = 'https://api.github.com/repos%s/issues/89' % (link)
        # address = 'https://api.github.com/repos%s/contributors' % ('/Arjun-Code-Knight/csc510-se-project')
        # abelList = dumpLables(address)
        #labelLists.append(labelList)
        #time.sleep(5)
        dumpfile = dumpIssues(links_to_repo.index(groupname),groupname, \
            address_issues,labelLists[links_to_repo.index(groupname)],\
            groupIDdic[groupname])
    #f = open("LablesLists", 'w')
    #pickle.dump(labelLists,f)
    #f.close()
    #print (labelLists)
 
BadSmellFiles = open("IssueBadSmell.csv", "w")
BadSmellFiles.write( ",Uneven contribution on assigning issues,  \
    Unusual activity of open issues, \
    Number of weeks has unusually open issues activity,\
    Unusual activity of close issue,\
    Number of weeks has unusually close issues activity,\
    percentage of Issues with unusually long or short lasting time, \
    Unclosed issues after April 9, \
    Percentage of issues closed after milestone deadline, \
    Percentage of issues without comments, \
    Percentage of issues without milestone label, \
    Percentage of issues without any label, \
    Percentage of issues without assignee, \
    Number of unused labels counts,\
    Total number of issues,\
    Total number of labels, \n" )       
launchDump()
BadSmellFiles.close()


    
     
 
