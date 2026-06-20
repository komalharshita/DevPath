import json

def check_duplicates():
    with open("data/projects.json", "r", encoding="utf-8") as f:
        projects = json.load(f)
    print(f"Total projects: {len(projects)}")
    
    ids = {}
    for p in projects:
        pid = p.get("id")
        if pid in ids:
            ids[pid].append(p.get("title"))
        else:
            ids[pid] = [p.get("title")]
            
    for pid, titles in ids.items():
        if len(titles) > 1:
            print(f"ID {pid} has duplicates: {titles}")

if __name__ == '__main__':
    check_duplicates()
