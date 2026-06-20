import json

def print_ids():
    with open("data/projects.json", "r", encoding="utf-8") as f:
        projects = json.load(f)
    for p in projects:
        print(f"ID={p.get('id')} | Title={p.get('title')}")

if __name__ == '__main__':
    print_ids()
