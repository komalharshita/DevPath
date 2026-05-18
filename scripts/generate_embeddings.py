import json
import os
import pickle
import sys

# Append parent directory to path so script can access the utils folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.embedding_helpers import get_embedding

PROJECTS_JSON_PATH = "data/projects.json"
EMBEDDINGS_PKL_PATH = "data/project_embeddings.pkl"

def build_project_context(project: dict) -> str:
    """Concatenates project metadata into a rich contextual text string."""
    title = project.get("title", "")
    description = project.get("description", "")
    tags = ", ".join(project.get("tags", []))

    # Extracting nested goals or steps if they exist in your json schema
    steps = ""
    if "steps" in project:
        steps = " Tasks: " + " ".join([s.get("title", "") for s in project["steps"]])

    return f"Title: {title}. Description: {description}. Tags: {tags}.{steps}"

def main():
    if not os.path.exists(PROJECTS_JSON_PATH):
        print(f"Error: Could not find {PROJECTS_JSON_PATH}")
        return

    with open(PROJECTS_JSON_PATH, "r") as f:
        projects = json.load(f)

    print(f"Loaded {len(projects)} projects. Generating semantic embeddings...")

    embedded_dataset = []

    for idx, project in enumerate(projects):
        try:
            context_string = build_project_context(project)
            print(f"[{idx + 1}/{len(projects)}] Vectorizing: {project.get('title')}")

            vector = get_embedding(context_string)

            # Keep a tracking map associating the project ID with its vector coordinates
            embedded_dataset.append({
                "id": project.get("id"),
                "title": project.get("title"),
                "vector": vector
            })
        except Exception as e:
            print(f"Failed to embed project {project.get('title')}: {e}")
            return

    # Store the generated vectors as a static binary asset
    with open(EMBEDDINGS_PKL_PATH, "wb") as f:
        pickle.dump(embedded_dataset, f)

    print(f"Successfully saved pre-computed semantic matrix to {EMBEDDINGS_PKL_PATH}!")

if __name__ == "__main__":
    main()