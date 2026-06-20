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
        # Search body
        body = pr.get('body') or ''
        for match in pattern.findall(body):
            referenced.add(int(match))
        # Also search title
        title = pr.get('title') or ''
        for match in pattern.findall(title):
            referenced.add(int(match))
        for match in number_pattern.findall(title):
            referenced.add(int(match))
    return referenced

def triage():
    print("Fetching open pull requests...")
    pulls = fetch_json("https://api.github.com/repos/komalharshita/devpath/pulls?state=open&per_page=100")
    referenced = get_referenced_issues(pulls)
    print(f"Found {len(pulls)} open PRs, referencing issues: {referenced}")

    print("Fetching open issues...")
    # Get up to 100 open issues
    issues = fetch_json("https://api.github.com/repos/komalharshita/devpath/issues?state=open&per_page=100")
    
    candidates = []
    for issue in issues:
        if 'pull_request' in issue:
            continue
        
        num = issue.get('number')
        title = issue.get('title')
        assignees = issue.get('assignees', [])
        labels = [l['name'].lower() for l in issue.get('labels', [])]
        
        # Must have gssoc-2026 or gssoc-26 or GSSoC26
        gssoc_labels = [l for l in labels if 'gssoc' in l]
        if not gssoc_labels:
            continue
            
        # Filter: no assignee
        if assignees:
            continue
            
        # Filter: no open PR referencing it
        if num in referenced:
            continue
            
        # Score priority
        # 1. good first issue + beginner
        # 2. bug
        # 3. documentation
        # 4. intermediate
        # 5. advanced
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
            'primary_label': primary_label
        })
        
    candidates.sort(key=lambda x: (x['priority'], x['number']))
    
    print("\nTriaged candidates:")
    print(f"{'#':<4} | {'Issue #':<8} | {'Title':<50} | {'Label':<15} | {'Priority':<8}")
    print("-" * 95)
    for idx, c in enumerate(candidates):
        print(f"{idx+1:<4} | {c['number']:<8} | {c['title'][:50]:<50} | {c['primary_label']:<15} | {c['priority']:<8}")

if __name__ == '__main__':
    triage()
