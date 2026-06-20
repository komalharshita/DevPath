import urllib.request
import json
import re

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def get_referenced_issues(pulls):
    referenced = set()
    pattern = re.compile(r'(?:closes|fixes|resolves)\s+#(\d+)', re.IGNORECASE)
    number_pattern = re.compile(r'#(\d+)')
    for pr in pulls:
        body = pr.get('body') or ''
        for match in pattern.findall(body):
            referenced.add(int(match))
        title = pr.get('title') or ''
        for match in pattern.findall(title):
            referenced.add(int(match))
        for match in number_pattern.findall(title):
            referenced.add(int(match))
    return referenced

def triage_all():
    print("Fetching all open PRs...")
    pulls = []
    page = 1
    while True:
        p = fetch_json(f"https://api.github.com/repos/komalharshita/devpath/pulls?state=open&per_page=100&page={page}")
        if not p:
            break
        pulls.extend(p)
        page += 1
    referenced = get_referenced_issues(pulls)
    print(f"Total open PRs: {len(pulls)}, referencing: {referenced}")

    print("Fetching all open issues...")
    issues = []
    page = 1
    while True:
        p = fetch_json(f"https://api.github.com/repos/komalharshita/devpath/issues?state=open&per_page=100&page={page}")
        if not p:
            break
        issues.extend(p)
        page += 1
        
    candidates = []
    for issue in issues:
        if 'pull_request' in issue:
            continue
        
        num = issue.get('number')
        title = issue.get('title')
        assignees = issue.get('assignees', [])
        labels = [l['name'].lower() for l in issue.get('labels', [])]
        
        gssoc_labels = [l for l in labels if 'gssoc' in l]
        if not gssoc_labels:
            continue
            
        # Check if assignees is empty
        has_assignee = len(assignees) > 0
        has_pr = num in referenced
        
        # Priority mapping
        priority = 99
        primary_label = "other"
        
        if any(x in labels for x in ['good first issue', 'level:beginner', 'beginner']):
            priority = 1
            primary_label = "beginner"
        elif any(x in labels for x in ['bug', 'type:bug']):
            priority = 2
            primary_label = "bug"
        elif any(x in labels for x in ['documentation', 'type:docs', 'docs']):
            priority = 3
            primary_label = "docs"
        elif any(x in labels for x in ['intermediate', 'level:intermediate']):
            priority = 4
            primary_label = "intermediate"
        elif any(x in labels for x in ['advanced', 'level:advanced']):
            priority = 5
            primary_label = "advanced"
            
        candidates.append({
            'number': num,
            'title': title,
            'labels': [l['name'] for l in issue.get('labels', [])],
            'priority': priority,
            'primary_label': primary_label,
            'has_assignee': has_assignee,
            'has_pr': has_pr,
            'assignees': [a['login'] for a in assignees]
        })
        
    # Print statistics
    print(f"Total open GSSoC issues: {len(candidates)}")
    print(f"Unassigned: {len([c for c in candidates if not c['has_assignee']])}")
    print(f"Unreferenced: {len([c for c in candidates if not c['has_pr']])}")
    print(f"Both unassigned and unreferenced: {len([c for c in candidates if not c['has_assignee'] and not c['has_pr']])}")
    
    print("\nCandidates details (first 30):")
    for idx, c in enumerate(candidates[:30]):
        print(f"#{c['number']} | Assigned: {c['has_assignee']} ({c['assignees']}) | Has PR: {c['has_pr']} | Title: {c['title'][:50]}")

if __name__ == '__main__':
    triage_all()
