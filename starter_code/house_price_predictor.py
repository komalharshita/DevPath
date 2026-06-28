"""
house_price_predictor.py
========================
Project:    House Price Prediction Model
Difficulty: Intermediate
Skills:     Python, pandas, scikit-learn, matplotlib
Time:       High (5-7 days)

What you will build:
    A machine learning regression model that predicts house prices based on
    features like square footage, number of bedrooms, location, age, etc.
    You will load real estate data, clean and preprocess it, train a linear
    regression and gradient boosting models, evaluate them with metrics like
    MAE (Mean Absolute Error) and R² score, and use the model to predict
    prices for new houses.

    This project teaches the full ML regression workflow: data loading →
    exploratory analysis → feature engineering → model selection → evaluation
    → prediction. You will also learn to visualise results with matplotlib.

How to run:
    pip install pandas scikit-learn matplotlib
    python house_price_predictor.py
    View training plots and predictions in the terminal and generated images.

Learning goals:
    - Understanding regression vs classification (prediction vs categories)
    - Loading, inspecting, and cleaning real estate data
    - Feature engineering: creating meaningful features from raw data
    - Train/test split and cross-validation for robust evaluation
    - Comparing multiple models (Linear Regression vs Gradient Boosting)
    - Interpreting regression metrics: MAE, RMSE, R² score
    - Visualising predictions vs actual prices using matplotlib
    - Identifying and handling outliers in real data

Key concept — Regression in plain English:
    Regression predicts a continuous numeric value (price) based on input
    features. Unlike classification (which predicts categories like spam/ham),
    regression outputs a real number.

    Linear Regression assumes a straight-line relationship:
        price = w₀ + w₁×sqft + w₂×bedrooms + w₃×age + ...

    Gradient Boosting builds an ensemble of weak learners (decision trees)
    that correct each other's mistakes, often achieving better accuracy.

    Both models learn from training data to estimate unknown prices on new
    houses — the true test of a good model.

Data flow:
    Raw house dataset (CSV)
        |
        v
    load_dataset()           <- read CSV, check for nulls            [TODO]
        |
        v
    explore_data()           <- summary stats, visualisations         [DONE]
        |
        v
    preprocess_data()        <- handle missing values, scale features [TODO]
        |
        v
    select_features()        <- choose which columns to use           [TODO]
        |
        v
    split_data()             <- train/test split                      [DONE]
        |
        v
    train_linear_model()     <- fit Linear Regression                 [TODO]
        |
        v
    train_boosting_model()   <- fit Gradient Boosting                 [TODO]
        |
        v
    evaluate_models()        <- compute MAE, RMSE, R² on test data   [TODO]
        |
        v
    visualise_results()      <- plot predictions vs actual            [TODO]
        |
        v
    predict_house()          <- predict price for new house           [TODO]

Roadmap:
    Step 1:  Install dependencies and understand the data format
    Step 2:  Read and understand load_dataset() and explore_data()
    Step 3:  Complete preprocess_data() to handle missing/invalid values
    Step 4:  Complete select_features() to choose the most useful columns
    Step 5:  Complete train_linear_model() to fit a basic regression model
    Step 6:  Complete train_boosting_model() for an advanced ensemble model
    Step 7:  Complete evaluate_models() to compute error metrics
    Step 8:  Complete visualise_results() and predict_house()
"""

import csv
import math

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Random state ensures reproducible train/test splits.
RANDOM_STATE = 42

# Test set fraction (20% of data held for evaluation).
TEST_SIZE = 0.2

# Features to use for predictions (all numeric columns except target).
TARGET_COLUMN = "price"

# Maximum allowed age for a house (remove obvious data errors).
MAX_HOUSE_AGE = 200

# Minimum allowed price (remove data entry mistakes).
MIN_PRICE = 1000

# Maximum allowed price (remove outliers if needed).
MAX_PRICE = 10_000_000


# ---------------------------------------------------------------------------
# Data loading and exploration
# ---------------------------------------------------------------------------

def load_dataset(filepath):
    """
    Load house price dataset from a CSV file.

    Args:
        filepath (str): Path to CSV file. Expected columns include:
                        price, sqft, bedrooms, bathrooms, age, location, etc.

    Returns:
        pd.DataFrame: The loaded data with all rows and columns.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError:       If required columns are missing.

    TODO:
        1. Read the CSV file using pd.read_csv(filepath).
        2. Check that the TARGET_COLUMN ("price") exists.
           Raise ValueError with a helpful message if missing.
        3. Print basic info:
           - Number of rows and columns
           - Column names and types
           - First few rows (df.head())
        4. Return the DataFrame.

    Example:
        df = load_dataset("houses.csv")
        # -> DataFrame with shape (1000, 8)
    """
    # --- Write your data loading code here ---

    return pd.DataFrame()


def explore_data(df):
    """
    Produce summary statistics and basic visualisations of the dataset.

    Args:
        df (pd.DataFrame): The loaded house price data.

    Returns:
        None (prints to stdout and optionally saves plots).

    This function is already complete — read it to understand how
    df.describe(), df.isnull().sum(), and plt.hist() work.

    It demonstrates:
        - .describe() for numeric summaries (mean, std, min, max, quartiles)
        - .isnull().sum() to check for missing values
        - matplotlib histograms for distribution visualisation
    """
    print("\n" + "=" * 70)
    print("DATA EXPLORATION")
    print("=" * 70)

    print("\nDataset shape:", df.shape)
    print("\nFirst few rows:")
    print(df.head())

    print("\nColumn types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nStatistical summary:")
    print(df.describe())

    # Visualise price distribution
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.hist(df[TARGET_COLUMN], bins=50, edgecolor='black')
    plt.xlabel("Price ($)")
    plt.ylabel("Frequency")
    plt.title("Distribution of House Prices")

    # Visualise sqft vs price if sqft column exists
    if "sqft" in df.columns:
        plt.subplot(1, 2, 2)
        plt.scatter(df["sqft"], df[TARGET_COLUMN], alpha=0.5)
        plt.xlabel("Square Feet")
        plt.ylabel("Price ($)")
        plt.title("Price vs Square Footage")

    plt.tight_layout()
    plt.savefig("exploration.png")
    print("\n✓ Saved exploration plot to exploration.png")
    plt.close()


# ---------------------------------------------------------------------------
# Data preprocessing
# ---------------------------------------------------------------------------

def preprocess_data(df):
    """
    Clean and prepare the dataset for model training.

    Args:
        df (pd.DataFrame): Raw data from load_dataset().

    Returns:
        pd.DataFrame: Cleaned data ready for feature selection and training.

    Preprocessing steps:
        1. Remove rows where the target (price) is missing.
        2. Remove rows with invalid prices (< MIN_PRICE or > MAX_PRICE).
        3. Remove rows with invalid age (> MAX_HOUSE_AGE).
        4. Handle missing values in numeric columns (fill with median).
        5. Remove any duplicate rows.

    TODO:
        1. Create a copy: df = df.copy()
        2. Drop rows where TARGET_COLUMN is NaN:
           df = df.dropna(subset=[TARGET_COLUMN])
        3. Remove invalid price rows:
           df = df[df[TARGET_COLUMN] >= MIN_PRICE]
           df = df[df[TARGET_COLUMN] <= MAX_PRICE]
        4. If "age" column exists, remove rows where age > MAX_HOUSE_AGE:
           if "age" in df.columns:
               df = df[df["age"] <= MAX_HOUSE_AGE]
        5. Fill missing numeric values with median:
           numeric_cols = df.select_dtypes(include=['number']).columns
           for col in numeric_cols:
               df[col].fillna(df[col].median(), inplace=True)
        6. Drop duplicate rows:
           df = df.drop_duplicates()
        7. Print the shape before and after cleaning.
        8. Return df.

    Example:
        df = preprocess_data(df)
        # -> Removes 50 rows with missing/invalid data; 950 rows remain
    """
    print("\n" + "=" * 70)
    print("DATA PREPROCESSING")
    print("=" * 70)

    original_shape = df.shape
    print(f"\nOriginal shape: {original_shape}")

    # --- Write your preprocessing code here ---

    print(f"Final shape after cleaning: {df.shape}")
    print(f"Rows removed: {original_shape[0] - df.shape[0]}")

    return df


def select_features(df):
    """
    Choose numeric features for the model and split into X and y.

    Args:
        df (pd.DataFrame): Preprocessed data from preprocess_data().

    Returns:
        tuple: (X, y)
            X (pd.DataFrame): Feature matrix (all numeric columns except target).
            y (pd.Series):    Target vector (the price column).

    Feature selection:
        Keep all numeric columns except the target. Drop non-numeric columns
        (like location names unless they were pre-encoded as numbers).

    TODO:
        1. Extract the target: y = df[TARGET_COLUMN]
        2. Extract features: X = df.drop(columns=[TARGET_COLUMN])
        3. Keep only numeric columns in X:
           numeric_cols = X.select_dtypes(include=['number']).columns
           X = X[numeric_cols]
        4. Print the feature names and X.shape.
        5. Return (X, y).

    Example:
        X, y = select_features(df)
        # -> X shape: (950, 5), y shape: (950,)
        # -> Features: ['sqft', 'bedrooms', 'bathrooms', 'age', 'garage']
    """
    print("\n" + "=" * 70)
    print("FEATURE SELECTION")
    print("=" * 70)

    # --- Write your feature selection code here ---

    return None, None


def split_data(X, y):
    """
    Divide data into training and test sets.

    Args:
        X (pd.DataFrame): Feature matrix from select_features().
        y (pd.Series):    Target vector.

    Returns:
        tuple: (X_train, X_test, y_train, y_test)

    This function is already complete — it uses sklearn's standard split.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    print(f"\nTrain set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")

    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

def train_linear_model(X_train, y_train):
    """
    Train a Linear Regression model on training data.

    Args:
        X_train (pd.DataFrame): Training features.
        y_train (pd.Series):    Training target values (prices).

    Returns:
        tuple: (model, scaler)
            model (LinearRegression): Fitted regression model.
            scaler (StandardScaler):  Fitted feature scaler (for consistency).

    Why scaling matters:
        Linear Regression's coefficients are sensitive to feature scale.
        If sqft ranges 1000–5000 and bedrooms ranges 1–5, sqft will
        dominate the model. StandardScaler normalises features to mean=0,
        std=1, making coefficients comparable.

    TODO:
        1. Create a StandardScaler instance: scaler = StandardScaler()
        2. Fit and transform training features:
           X_train_scaled = scaler.fit_transform(X_train)
        3. Create a LinearRegression instance: model = LinearRegression()
        4. Fit the model: model.fit(X_train_scaled, y_train)
        5. Return (model, scaler).

    Note: The scaler must be returned because test data will use the same
          scaling during evaluation and prediction.
    """
    print("\n" + "=" * 70)
    print("TRAINING LINEAR REGRESSION")
    print("=" * 70)

    # --- Write your linear regression training code here ---

    return None, None


def train_boosting_model(X_train, y_train, scaler):
    """
    Train a Gradient Boosting Regressor on training data.

    Args:
        X_train (pd.DataFrame): Training features.
        y_train (pd.Series):    Training target values.
        scaler (StandardScaler): Feature scaler from train_linear_model().

    Returns:
        GradientBoostingRegressor: Fitted boosting model.

    Why Gradient Boosting?
        Boosting trains multiple weak learners (shallow decision trees) that
        correct each other's mistakes. Each tree learns the residuals (errors)
        of the previous tree, leading to better predictions than a single tree.

    Hyperparameters:
        - n_estimators: number of trees (more = slower but potentially better)
        - learning_rate: shrinkage (smaller = slower learning, less overfitting)
        - max_depth: tree depth (shallower = less complex, more generalisation)

    TODO:
        1. Scale training features using scaler.transform(X_train).
        2. Create a GradientBoostingRegressor with reasonable hyperparameters:
           model = GradientBoostingRegressor(
               n_estimators=100,
               learning_rate=0.1,
               max_depth=5,
               random_state=RANDOM_STATE
           )
        3. Fit the model: model.fit(X_train_scaled, y_train)
        4. Return the fitted model.

    Note: Unlike linear regression, tree-based models don't require scaling,
          but we still scale for consistency with the pipeline.
    """
    print("\n" + "=" * 70)
    print("TRAINING GRADIENT BOOSTING")
    print("=" * 70)

    # --- Write your gradient boosting training code here ---

    return None


# ---------------------------------------------------------------------------
# Model evaluation
# ---------------------------------------------------------------------------

def evaluate_models(linear_model, boosting_model, X_test, y_test, scaler):
    """
    Assess both models on held-out test data and compare performance.

    Args:
        linear_model (LinearRegression):        Fitted linear model.
        boosting_model (GradientBoostingRegressor): Fitted boosting model.
        X_test (pd.DataFrame):                  Test features.
        y_test (pd.Series):                     Test targets.
        scaler (StandardScaler):                Fitted scaler from training.

    Returns:
        dict: Results with keys like "linear_mae", "linear_rmse", "linear_r2",
              "boosting_mae", "boosting_rmse", "boosting_r2".

    Regression metrics:
        - MAE (Mean Absolute Error): Average absolute difference.
          Lower is better. Easy to interpret (in original units).
        - RMSE (Root Mean Squared Error): Root of average squared difference.
          Penalises large errors more than MAE. Lower is better.
        - R² (Coefficient of Determination): Fraction of variance explained.
          Higher is better (max 1.0). Often more intuitive than MAE/RMSE.

    TODO:
        1. Scale test features: X_test_scaled = scaler.transform(X_test)
        2. Predict with linear model:
           y_pred_linear = linear_model.predict(X_test_scaled)
        3. Predict with boosting model:
           y_pred_boosting = boosting_model.predict(X_test_scaled)
        4. Compute metrics for linear model using mean_absolute_error(),
           mean_squared_error(), and r2_score() (all already imported).
           mae = mean_absolute_error(y_test, y_pred_linear)
           rmse = math.sqrt(mean_squared_error(y_test, y_pred_linear))
           r2 = r2_score(y_test, y_pred_linear)
        5. Do the same for boosting model.
        6. Print both sets of metrics in a nice format.
        7. Return a dict with all six metrics.

    Example output:
        Linear Regression:
          MAE: $45,234
          RMSE: $67,891
          R²: 0.7823
        Gradient Boosting:
          MAE: $32,456
          RMSE: $51,234
          R²: 0.8901
    """
    print("\n" + "=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)

    # --- Write your evaluation code here ---

    return {}


# ---------------------------------------------------------------------------
# Visualisation and prediction
# ---------------------------------------------------------------------------

def visualise_results(linear_model, boosting_model, X_test, y_test, scaler):
    """
    Create scatter plots comparing predicted vs actual prices.

    Args:
        linear_model (LinearRegression):        Fitted model.
        boosting_model (GradientBoostingRegressor): Fitted model.
        X_test (pd.DataFrame):                  Test features.
        y_test (pd.Series):                     Test targets.
        scaler (StandardScaler):                Fitted scaler.

    Returns:
        None (saves plots to PNG files).

    Visualisation shows:
        - X-axis: actual prices
        - Y-axis: predicted prices
        - If prediction is perfect, all points lie on the y=x diagonal.
        - Points above the line: underestimated prices.
        - Points below the line: overestimated prices.

    TODO:
        1. Scale test features.
        2. Get predictions from both models.
        3. Create a figure with two subplots (side by side).
        4. Left subplot:
           plt.scatter(y_test, y_pred_linear, alpha=0.5)
           plt.plot([y_test.min(), y_test.max()],
                    [y_test.min(), y_test.max()], "r--", lw=2)
           (the red line is the perfect prediction diagonal)
           plt.xlabel("Actual Price")
           plt.ylabel("Predicted Price")
           plt.title("Linear Regression")
        5. Right subplot: same for boosting model.
        6. Save with plt.savefig("predictions.png")

    Example:
        visualise_results(model1, model2, X_test, y_test, scaler)
        # -> Saves "predictions.png"
    """
    print("\n" + "=" * 70)
    print("VISUALISING RESULTS")
    print("=" * 70)

    # --- Write your visualisation code here ---

    print("✓ Saved prediction plots to predictions.png")


def predict_house(linear_model, boosting_model, scaler, house_features):
    """
    Predict the price of a single new house.

    Args:
        linear_model (LinearRegression):        Fitted model.
        boosting_model (GradientBoostingRegressor): Fitted model.
        scaler (StandardScaler):                Fitted scaler.
        house_features (dict):                  Feature values for the house.
                                                Example: {"sqft": 2500, "bedrooms": 4, ...}

    Returns:
        dict: Predictions from both models, plus average.
              Keys: "linear_price", "boosting_price", "average_price"

    TODO:
        1. Convert house_features dict to a DataFrame with one row.
           Use: features_df = pd.DataFrame([house_features])
        2. Scale the features: features_scaled = scaler.transform(features_df)
        3. Predict with linear model: linear_pred = linear_model.predict(...)
        4. Predict with boosting model: boosting_pred = boosting_model.predict(...)
        5. Compute average: avg_pred = (linear_pred + boosting_pred) / 2
        6. Return dict with all three predictions (rounded to 2 decimals).

    Example:
        house = {"sqft": 2500, "bedrooms": 4, "bathrooms": 2, "age": 10, "garage": 2}
        result = predict_house(model1, model2, scaler, house)
        # -> {"linear_price": 425000, "boosting_price": 432000, "average_price": 428500}
    """
    # --- Write your prediction code here ---

    return {}


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main():
    """
    Orchestrate the full regression pipeline.

    This function is already complete — it shows how to wire all functions
    together. Just run:
        python house_price_predictor.py
    """
    print("\n" + "=" * 70)
    print("HOUSE PRICE PREDICTION MODEL")
    print("=" * 70)

    # --- Step 1: Load and explore ---
    try:
        df = load_dataset("houses.csv")
    except FileNotFoundError:
        print("\n✗ Error: houses.csv not found.")
        print("  Create a CSV file with columns: price, sqft, bedrooms, bathrooms, age, etc.")
        return

    explore_data(df)

    # --- Step 2: Preprocess ---
    df = preprocess_data(df)

    # --- Step 3: Select features and split ---
    X, y = select_features(df)
    if X is None or y is None:
        print("\n✗ select_features() returned None. Check your implementation.")
        return

    X_train, X_test, y_train, y_test = split_data(X, y)

    # --- Step 4: Train models ---
    linear_model, scaler = train_linear_model(X_train, y_train)
    if linear_model is None:
        print("\n✗ train_linear_model() returned None. Check your implementation.")
        return

    boosting_model = train_boosting_model(X_train, y_train, scaler)
    if boosting_model is None:
        print("\n✗ train_boosting_model() returned None. Check your implementation.")
        return

    # --- Step 5: Evaluate ---
    metrics = evaluate_models(linear_model, boosting_model, X_test, y_test, scaler)

    # --- Step 6: Visualise ---
    visualise_results(linear_model, boosting_model, X_test, y_test, scaler)

    # --- Step 7: Example prediction ---
    print("\n" + "=" * 70)
    print("EXAMPLE PREDICTION")
    print("=" * 70)
    example_house = {
        "sqft": 2500,
        "bedrooms": 4,
        "bathrooms": 2,
        "age": 10,
    }
    prediction = predict_house(linear_model, boosting_model, scaler, example_house)
    if prediction:
        print(f"\nHouse features: {example_house}")
        print(f"Linear Regression prediction: ${prediction['linear_price']:,.2f}")
        print(f"Gradient Boosting prediction: ${prediction['boosting_price']:,.2f}")
        print(f"Average prediction: ${prediction['average_price']:,.2f}")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Sample dataset (CSV format)
# ---------------------------------------------------------------------------
#
# Save this as "houses.csv" and run:  python house_price_predictor.py
#
# price,sqft,bedrooms,bathrooms,age,garage
# 350000,2000,3,2,15,2
# 425000,2500,4,2,10,2
# 320000,1800,3,1,25,1
# 550000,3200,4,3,5,3
# 280000,1500,2,1,30,1
# 480000,2800,4,2.5,8,2
# 360000,2100,3,2,12,2
# 620000,3500,5,3,2,3
# 270000,1400,2,1,35,1
# 410000,2400,4,2,11,2
# ... (add more examples as needed)
