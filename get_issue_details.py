import urllib.request
import json

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def get_details():
    target_issues = [747, 726, 725, 724, 712, 710, 702, 786, 475]
    out = []
    for num in target_issues:
        try:
            url = f"https://api.github.com/repos/komalharshita/devpath/issues/{num}"
            issue = fetch_json(url)
            out.append(f"## Issue #{num}: {issue.get('title')}")
            out.append(f"Labels: {[l['name'] for l in issue.get('labels', [])]}")
            out.append(f"Body:\n{issue.get('body')}\n")
            out.append("-" * 80)
        except Exception as e:
            print(f"Error fetching #{num}: {e}")
            
    with open("candidate_details.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Wrote candidate_details.md")

if __name__ == '__main__':
    get_details()
