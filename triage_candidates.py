import urllib.request
import json
import re

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    # retry up to 3 times
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            if i == 2:
                raise e
            print(f"Error fetching {url}, retrying... {e}")

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

def triage_candidates():
    print("Fetching page 1 of open PRs...")
    pulls = fetch_json("https://api.github.com/repos/komalharshita/devpath/pulls?state=open&per_page=100")
    referenced = get_referenced_issues(pulls)

    print("Fetching page 1 of open issues...")
    issues = fetch_json("https://api.github.com/repos/komalharshita/devpath/issues?state=open&per_page=100")
        
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
            
        # Filter: no assignee and no open PR
        if assignees or (num in referenced):
            continue
            
        # Priority mapping:
        # 1. good first issue / level:beginner / beginner
        # 2. bug / type:bug
        # 3. documentation / type:docs / docs
        # 4. intermediate / level:intermediate
        # 5. advanced / level:advanced
        priority = 99
        primary_label = "other"
        
        # Check beginner
        if any(x in labels for x in ['good first issue', 'level:beginner', 'beginner', 'good-first-issue']):
            priority = 1
            primary_label = "level:beginner"
        # Check bug
        elif any(x in labels for x in ['bug', 'type:bug']):
            priority = 2
            primary_label = "type:bug"
        # Check docs
        elif any(x in labels for x in ['documentation', 'type:docs', 'docs']):
            priority = 3
            primary_label = "type:docs"
        # Check intermediate
        elif any(x in labels for x in ['intermediate', 'level:intermediate']):
            priority = 4
            primary_label = "level:intermediate"
        # Check advanced
        elif any(x in labels for x in ['advanced', 'level:advanced']):
            priority = 5
            primary_label = "level:advanced"
            
        candidates.append({
            'number': num,
            'title': title,
            'labels': [l['name'] for l in issue.get('labels', [])],
            'priority': priority,
            'primary_label': primary_label
        })
        
    # Sort: priority ascending, then number descending (newest first)
    candidates.sort(key=lambda x: (x['priority'], -x['number']))
    
    print(f"\nTop 30 triaged candidates from Page 1 (newest first):")
    print(f"{'#':<4} | {'Issue #':<8} | {'Title':<50} | {'Label':<20} | {'Priority':<8}")
    print("-" * 105)
    for idx, c in enumerate(candidates[:30]):
        print(f"{idx+1:<4} | {c['number']:<8} | {c['title'][:50]:<50} | {c['primary_label']:<20} | {c['priority']:<8}")

if __name__ == '__main__':
    triage_candidates()
