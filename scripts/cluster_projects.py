"""
scripts/cluster_projects.py

Precomputes K-Means cluster assignments for all projects in data/projects.json
and writes the result to data/clusters.json.

Run this script whenever projects.json changes:
    python scripts/cluster_projects.py

Requirements:
    pip install scikit-learn

Output format (data/clusters.json):
    {
        "k": 4,
        "clusters": {
            "1": 0,
            "2": 2,
            ...
        },
        "members": {
            "0": [1, 7, 10],
            "1": [3, 9, 19],
            ...
        }
    }
"""

import json
import math
import os
import sys

# ---------------------------------------------------------------------------
# Try importing scikit-learn. Give a clear message if it is not installed.
# ---------------------------------------------------------------------------
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import MultiLabelBinarizer
except ImportError:
    sys.exit(
        "scikit-learn is required. Install it with:  pip install scikit-learn"
    )

# ---------------------------------------------------------------------------
# Paths — works whether you run the script from the repo root or from scripts/
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
PROJECTS_PATH = os.path.join(REPO_ROOT, "data", "projects.json")
CLUSTERS_PATH = os.path.join(REPO_ROOT, "data", "clusters.json")

# ---------------------------------------------------------------------------
# Minimum projects needed before clustering makes sense.
# Below this threshold the script exits with a clear explanation.
# ---------------------------------------------------------------------------
MIN_PROJECTS = 10


def load_projects(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def choose_k(n: int) -> int:
    """
    Pick a sensible number of clusters for n projects.

    Rule: k = max(2, round(sqrt(n / 2)))

    Examples:
        10 projects  -> k = 2
        18 projects  -> k = 3
        32 projects  -> k = 4
        50 projects  -> k = 5

    This keeps clusters from being either too broad (k=2 for 50 projects)
    or too granular (k=10 for 10 projects).
    """
    return max(2, round(math.sqrt(n / 2)))


def vectorise(projects: list[dict]):
    """
    Convert categorical project attributes into a numeric matrix.

    Each project becomes a binary vector with one dimension per unique value
    of: skills, level, interest, and time.

    Example row for a project with skills=["Python"], level="Beginner",
    interest="Data", time="Low":

        [Python=1, HTML=0, ..., Beginner=1, Intermediate=0, ..., Data=1, ...]

    Returns:
        X      -- numpy array of shape (n_projects, n_features)
        labels -- list of column names (for debugging)
    """
    mlb_skills = MultiLabelBinarizer()
    mlb_level = MultiLabelBinarizer()
    mlb_interest = MultiLabelBinarizer()
    mlb_time = MultiLabelBinarizer()

    skills_matrix = mlb_skills.fit_transform(
        [p["skills"] for p in projects]
    )
    level_matrix = mlb_level.fit_transform(
        [[p["level"]] for p in projects]
    )
    interest_matrix = mlb_interest.fit_transform(
        [[p["interest"]] for p in projects]
    )
    time_matrix = mlb_time.fit_transform(
        [[p["time"]] for p in projects]
    )

    import numpy as np
    X = np.hstack([skills_matrix, level_matrix, interest_matrix, time_matrix])

    labels = (
        list(mlb_skills.classes_)
        + list(mlb_level.classes_)
        + list(mlb_interest.classes_)
        + list(mlb_time.classes_)
    )

    return X, labels


def run_clustering(projects: list[dict], k: int) -> dict:
    """
    Run K-Means and return the cluster assignments as a dict.

    Returns a dict with three keys:
        k        -- the number of clusters used
        clusters -- {project_id: cluster_id, ...}
        members  -- {cluster_id: [project_id, ...], ...}
    """
    X, feature_labels = vectorise(projects)

    km = KMeans(
        n_clusters=k,
        n_init=20,       # run 20 times and keep the best result
        random_state=42, # reproducible output
    )
    km.fit(X)

    clusters: dict[str, int] = {}
    members: dict[str, list] = {str(i): [] for i in range(k)}

    for project, cluster_id in zip(projects, km.labels_):
        pid = str(project["id"])
        cid = int(cluster_id)
        clusters[pid] = cid
        members[str(cid)].append(project["id"])

    return {
        "k": k,
        "clusters": clusters,
        "members": members,
    }


def print_summary(result: dict, projects: list[dict]) -> None:
    """Print a human-readable summary of the clustering result."""
    id_to_title = {str(p["id"]): p["title"] for p in projects}
    print(f"\nClustered {len(result['clusters'])} projects into {result['k']} groups.\n")
    for cid, member_ids in result["members"].items():
        print(f"  Cluster {cid} ({len(member_ids)} projects):")
        for pid in member_ids:
            print(f"    - [{pid}] {id_to_title.get(str(pid), '?')}")
    print()


def main():
    # ------------------------------------------------------------------
    # 1. Load projects
    # ------------------------------------------------------------------
    if not os.path.exists(PROJECTS_PATH):
        sys.exit(f"projects.json not found at: {PROJECTS_PATH}")

    projects = load_projects(PROJECTS_PATH)

    # ------------------------------------------------------------------
    # 2. Guard: need enough projects for clustering to be meaningful
    # ------------------------------------------------------------------
    if len(projects) < MIN_PROJECTS:
        sys.exit(
            f"Only {len(projects)} project(s) found. "
            f"Clustering requires at least {MIN_PROJECTS}. "
            f"Add more projects to data/projects.json first."
        )

    # ------------------------------------------------------------------
    # 3. Choose k and run clustering
    # ------------------------------------------------------------------
    k = choose_k(len(projects))
    print(f"Found {len(projects)} projects. Using k={k} clusters.")

    result = run_clustering(projects, k)
    print_summary(result, projects)

    # ------------------------------------------------------------------
    # 4. Write output
    # ------------------------------------------------------------------
    with open(CLUSTERS_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Cluster assignments written to: {CLUSTERS_PATH}")


if __name__ == "__main__":
    main()