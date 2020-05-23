import csv
import requests


GITHUB_USER = 'USERNAME' # manually change
GITHUB_PASSWORD = 'PASSWORD'
REPO = 'k9mail/k-9'  # format is username/repo
ISSUES_FOR_REPO_URL = 'https://api.github.com/repos/%s/issues' % REPO
AUTH = (GITHUB_USER, GITHUB_PASSWORD)

def write_issues(response):
    "output a list of issues to csv"
    if not r.status_code == 200:
        raise Exception(r.status_code)
    for issue in r.json():
        # labels = issue['labels']
        # for label in labels:
        print (issue['number'])
        # if label['name'] == "Client Requested":
        csvout.writerow([issue['number'], issue['title'].encode('utf-8'), issue['body'].encode('utf-8'), issue['created_at'], issue['updated_at']])


r = requests.get(ISSUES_FOR_REPO_URL, auth=AUTH)
csvfile = '%s-issues.csv' % (REPO.replace('/', '-'))
csvout = csv.writer(open(csvfile, 'w'))
csvout.writerow(('id', 'Title', 'Body', 'Created At', 'Updated At'))
write_issues(r)

#more pages? examine the 'link' header returned
#if 'link' in r.headers:
#    pages = dict(
#        [(rel[6:-1], url[url.index('<')+1:-1]) for url, rel in
#            [link.split(';') for link in
#                r.headers['link'].split(',')]])
#    while 'last' in pages and 'next' in pages:
#        r = requests.get(pages['next'], auth=AUTH)
#        write_issues(r)
#        if pages['next'] == pages['last']:
#            break
