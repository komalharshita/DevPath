import urllib.request
import json

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def debug_issues():
    issues = fetch_json("https://api.github.com/repos/komalharshita/devpath/issues?state=open&per_page=100")
    print(f"Total open issues/PRs fetched: {len(issues)}")
    
    for issue in issues[:30]:
        is_pr = 'pull_request' in issue
        num = issue.get('number')
        title = issue.get('title')
        assignees = [a['login'] for a in issue.get('assignees', [])]
        labels = [l['name'] for l in issue.get('labels', [])]
        
        print(f"#{num} | PR: {is_pr} | Assignees: {assignees} | Labels: {labels} | Title: {title[:40]}")

if __name__ == '__main__':
    debug_issues()
