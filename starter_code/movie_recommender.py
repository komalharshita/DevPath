"""
movie_recommender.py
====================
Project:    Movie Recommendation System
Difficulty: Intermediate
Skills:     Python, pandas, scikit-learn, NumPy
Time:       High (a week or more)

What you will build:
    Build a movie recommendation system that suggests movies to users based 
    on ratings and similarity scores. The project introduces similarity 
    scoring, pandas data handling and basic recommendation logic.

How to run:
    pip install pandas scikit-learn numpy
    python movie_recommender.py

When prompted, enter a movie name and the program will display a list of similar movie recommendations.

A small sample movie dataset can be created manually to test the recommender before using larger datasets.

Learning goals:
    - Loading and preprocessing datasets with pandas
    - Understanding recommendation system basics
    - Organize movie features into a pandas DataFrame
    - Computing similarity scores between movies
    - Building recommendation functions using Python

Roadmap:
    Step 1:  Load the movie ratings dataset using pandas
    Step 2:  Clean missing or invalid movie entries
    Step 3:  Organize movie features into a pandas DataFrame
    Step 4:  Compute similarity scores between movies
    Step 5:  Build a function to recommend similar movies
    Step 6:  Allow user input for selecting a movie
    Step 7:  Display top recommended movies and test with different inputs
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------------------------------------------
# Sample dataset
# -------------------------------------------------------------------

movies_data = {
    "Movie": [
        "Inception",
        "Interstellar",
        "The Dark Knight",
        "Titanic",
        "Avatar",
        "The Matrix"
    ],
    "Action": [9, 8, 10, 2, 7, 10],
    "SciFi": [10, 10, 6, 1, 9, 10],
    "Romance": [2, 1, 1, 10, 4, 1]
}
# TODO:
# Expand the dataset with more movies
# Load movie data from a CSV file
# Add more movie features for better recommendations

# -------------------------------------------------------------------
# Core Functions
# -------------------------------------------------------------------

def load_dataset():
    """
    Load the movie dataset into a pandas DataFrame.
    """
    df = pd.DataFrame(movies_data)
    return df


def preprocess_data(df):
    """
    Prepare feature data for similarity calculations.

    Returns:
        movie_titles (list)
        feature_matrix (DataFrame)
    """
    movie_titles = df["Movie"]
    feature_matrix = df.drop(columns=["Movie"])

    return movie_titles, feature_matrix


def calculate_similarity(feature_matrix):
    """
    Calculate cosine similarity between all movies.
    """
    similarity_matrix = cosine_similarity(feature_matrix)

    return similarity_matrix


def recommend_movies(movie_name, movie_titles, similarity_matrix):
    """
    Recommend similar movies based on cosine similarity.
    """
    if movie_name not in movie_titles.values:
        print("\nMovie not found. Please choose a movie from the list.")
        return

    movie_index = movie_titles[movie_titles == movie_name].index[0]

    similarity_scores = list(enumerate(similarity_matrix[movie_index]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    print(f"\nRecommended movies for '{movie_name}':\n")

    count = 0

    for index, score in similarity_scores[1:]:
        print(f"- {movie_titles[index]} (Similarity Score: {score:.2f})")

        count += 1

        if count == 3:
            break
        
    # TODO:
    # Allow users to filter recommendations by genre
    # Display more recommendation details
    
    
# -------------------------------------------------------------------
# Main Program
# -------------------------------------------------------------------

def main():
    """
    Run the movie recommendation system.
    """

    print("\n" + "=" * 50)
    print("     DevPath — Movie Recommendation System")
    print("=" * 50)

    # Step 1: Load dataset
    df = load_dataset()

    print("\nAvailable movies:")
    for movie in df["Movie"]:
        print(f"- {movie}")

    # Step 2: Preprocess data
    movie_titles, feature_matrix = preprocess_data(df)

    # Step 3: Calculate similarity
    similarity_matrix = calculate_similarity(feature_matrix)

    # Step 4: User input
    movie_name = input(
        "\nEnter a movie name for recommendations: "
    ).strip()

    if not movie_name:
        print("No movie entered.")
        return

    # Step 5: Generate recommendations
    recommend_movies(
        movie_name,
        movie_titles,
        similarity_matrix
    )

    print("\nRecommendation process complete.\n")


if __name__ == "__main__":
    main()