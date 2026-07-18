"""
image_classifier.py
===================
Project:    Image Classification with Deep Learning
Difficulty: Intermediate
Skills:     Python, TensorFlow/Keras, OpenCV, NumPy
Time:       High (6-8 days)

What you will build:
    A deep neural network that learns to classify images into categories
    (e.g., cats vs dogs, handwritten digits 0-9, etc.). You will use
    TensorFlow's Keras API to build and train a convolutional neural network
    (CNN), preprocess images using OpenCV, evaluate the model on a test set,
    and use it to classify new images.

    This project teaches: image loading and preprocessing, neural network
    architecture design, training loops, loss/accuracy tracking, and inference.

How to run:
    pip install tensorflow opencv-python numpy matplotlib
    python image_classifier.py
    (Ensure you have a dataset in ./data/train and ./data/test directories)

Learning goals:
    - Understanding how neural networks process images (tensors)
    - Image preprocessing: resizing, normalisation, augmentation
    - Building CNN architectures: convolutional + pooling + dense layers
    - Training neural networks: epochs, batches, overfitting
    - Evaluating classification: accuracy, loss curves, confusion matrices
    - Making predictions on new images
    - Saving and loading trained models for reuse

Key concept — Convolutional Neural Networks in plain English:
    A CNN learns hierarchical visual features:

    Layer 1 (Convolutional):
        Detects low-level features: edges, corners, textures.
        A "filter" slides across the image, computing local patterns.

    Layer 2 (Pooling):
        Downsamples the image (e.g., max pooling takes the brightest pixel
        in each 2×2 region). Reduces size, keeps important features.

    Layer 3 (Convolutional):
        Detects higher-level features: shapes, parts (eyes, nose, wheels).

    Layer N (Dense/Fully-connected):
        Combines all features to make the final classification decision.

    The network learns which filters and weights maximise accuracy on
    training data, then generalises to new, unseen images.

Data flow:
    Image files (train & test directories)
        |
        v
    load_images()            <- read image files from disk              [TODO]
        |
        v
    preprocess_images()      <- resize, normalise, convert to tensors   [TODO]
        |
        v
    build_model()            <- create CNN architecture                 [TODO]
        |
        v
    train_model()            <- fit network on training data            [TODO]
        |
        v
    evaluate_model()         <- compute accuracy, loss on test set      [TODO]
        |
        v
    visualise_training()     <- plot loss/accuracy curves               [DONE]
        |
        v
    predict_image()          <- classify a new image                    [TODO]
        |
        v
    Output class + confidence

Roadmap:
    Step 1:  Install dependencies (TensorFlow, OpenCV, numpy)
    Step 2:  Organise dataset into train/test directory structure
    Step 3:  Read and understand load_images() and preprocess_images()
    Step 4:  Complete preprocess_images() to resize and normalise
    Step 5:  Complete build_model() to create the CNN architecture
    Step 6:  Complete train_model() to fit the network
    Step 7:  Complete evaluate_model() to assess performance
    Step 8:  Complete predict_image() for inference on new images
"""

import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.preprocessing import LabelEncoder


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Input image dimensions (all images resized to this size).
IMAGE_HEIGHT = 128
IMAGE_WIDTH = 128
CHANNELS = 3  # RGB

# Training hyperparameters.
BATCH_SIZE = 32
EPOCHS = 10
VALIDATION_SPLIT = 0.2  # 20% of training data used for validation.
RANDOM_STATE = 42

# Paths to data directories.
TRAIN_DIR = "./data/train"
TEST_DIR = "./data/test"

# Output paths.
MODEL_PATH = "image_classifier_model.h5"
METRICS_PATH = "training_metrics.png"


# ---------------------------------------------------------------------------
# Image loading and preprocessing
# ---------------------------------------------------------------------------

def load_images(directory, max_images=None):
    """
    Load all images from a directory into memory.

    Args:
        directory (str):  Path to directory containing image files
                          (expects subdirectories for each class).
        max_images (int): Maximum number of images to load (None = load all).

    Returns:
        tuple: (images, labels, class_names)
            images (np.ndarray):      Array of shape (N, H, W, C) — N images,
                                      H×W pixels, C channels (RGB).
            labels (np.ndarray):      Array of shape (N,) with class indices.
            class_names (list[str]):  List of class names (folder names).

    Directory structure expected:
        data/train/
            cats/
                image1.jpg
                image2.jpg
            dogs/
                image1.jpg
                image2.jpg

    TODO:
        1. Get list of subdirectories (classes) using os.listdir(directory).
           Sort them alphabetically for consistency.
        2. Initialise empty lists: images = [], labels = [], class_names = []
        3. For each class folder:
           a. Get the full path: class_path = os.path.join(directory, class_name)
           b. For each image file in the class folder:
              - Read the image using cv2.imread(image_path).
              - Skip if the image is None (corrupted file).
              - Resize to (IMAGE_HEIGHT, IMAGE_WIDTH) using cv2.resize().
              - Append to images list.
              - Append the class index to labels list.
              - Increment a counter; stop when max_images is reached.
        4. Convert lists to numpy arrays:
           images = np.array(images)
           labels = np.array(labels)
        5. Print summary info (number of images per class).
        6. Return (images, labels, class_names).

    Example:
        imgs, lbls, names = load_images("data/train")
        # -> imgs shape: (1000, 128, 128, 3)
        # -> names: ["cats", "dogs"]
    """
    # --- Write your image loading code here ---

    return np.array([]), np.array([]), []


def preprocess_images(images):
    """
    Normalise pixel values and prepare images for the neural network.

    Args:
        images (np.ndarray): Array of shape (N, H, W, C) with pixel values 0–255.

    Returns:
        np.ndarray: Normalised array with pixel values in range [0, 1].

    Why normalisation matters:
        Raw pixel values (0–255) are on a very different scale than typical
        neural network weights (~0.1 to 1.0). This mismatch can slow training.
        Dividing by 255 rescales to [0, 1], making optimisation faster and
        more stable.

    TODO:
        1. Convert images to float32 type:
           images = images.astype(np.float32)
        2. Divide by 255 to scale to [0, 1]:
           images = images / 255.0
        3. Return the normalised images.

    Example:
        raw = np.array([[[255, 128, 0]]])  # shape (1, 1, 3)
        norm = preprocess_images(raw)
        # -> [[[[1.0, 0.502, 0.0]]]]  # same shape, different scale
    """
    # --- Write your preprocessing code here ---

    return images


# ---------------------------------------------------------------------------
# Model building
# ---------------------------------------------------------------------------

def build_model(input_shape, num_classes):
    """
    Construct a convolutional neural network for image classification.

    Args:
        input_shape (tuple): Shape of input images (H, W, C).
        num_classes (int):   Number of output classes.

    Returns:
        keras.Model: Uncompiled neural network model.

    CNN architecture to implement:
        Layer 1: Conv2D (32 filters, 3×3 kernel) + ReLU + MaxPooling (2×2)
        Layer 2: Conv2D (64 filters, 3×3 kernel) + ReLU + MaxPooling (2×2)
        Layer 3: Conv2D (128 filters, 3×3 kernel) + ReLU + MaxPooling (2×2)
        Layer 4: Flatten (reshape to 1D vector)
        Layer 5: Dense (256 units) + ReLU + Dropout (0.5)
        Layer 6: Dense (num_classes units) + Softmax

    Why this architecture:
        - Conv2D: extracts spatial features with learned filters.
        - ReLU: non-linearity allows learning complex patterns.
        - MaxPooling: reduces spatial size, keeps important features.
        - Flatten: converts 2D feature maps to 1D vector for classification.
        - Dense: combines features to make class predictions.
        - Dropout: randomly drops activations during training to prevent
          overfitting (forces network to learn redundant representations).
        - Softmax: outputs probabilities for each class.

    TODO:
        1. Use keras.Sequential() to create a model with layers in order.
        2. Add Conv2D layer:
           layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape)
        3. Add MaxPooling2D: layers.MaxPooling2D((2, 2))
        4. Repeat Conv2D+Pooling (same pattern) for 64 filters, then 128 filters.
        5. Add Flatten: layers.Flatten()
        6. Add Dense: layers.Dense(256, activation='relu')
        7. Add Dropout: layers.Dropout(0.5)
        8. Add output Dense: layers.Dense(num_classes, activation='softmax')
        9. Return the model.

    Example:
        model = build_model((128, 128, 3), 2)
        model.summary()  # print architecture
        # -> Model has ~2 million parameters
    """
    # --- Write your model building code here ---

    return None


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------

def train_model(model, X_train, y_train):
    """
    Train the neural network on training data.

    Args:
        model (keras.Model):      Compiled model (ready to train).
        X_train (np.ndarray):     Training images.
        y_train (np.ndarray):     Training labels.

    Returns:
        keras.callbacks.History: Training history object with loss/accuracy
                                 at each epoch.

    Training process:
        1. Model makes predictions on training batch.
        2. Compute loss (how wrong the predictions are).
        3. Compute gradients (direction to adjust weights).
        4. Update weights using gradient descent.
        5. Repeat for next batch until all training data is processed
           (one epoch).
        6. Repeat for EPOCHS iterations.

    TODO:
        1. Call model.fit() with:
           - X_train: training images
           - y_train: training labels (one-hot encoded or integer classes)
           - epochs=EPOCHS
           - batch_size=BATCH_SIZE
           - validation_split=VALIDATION_SPLIT
           - verbose=1 (show progress bar)
        2. Assign the result to history variable.
        3. Return history.

    Example:
        history = train_model(model, X_train, y_train)
        # -> model learns from data; history tracks loss/accuracy
    """
    # --- Write your training code here ---

    return None


# ---------------------------------------------------------------------------
# Model evaluation and visualisation
# ---------------------------------------------------------------------------

def evaluate_model(model, X_test, y_test):
    """
    Assess model performance on held-out test data.

    Args:
        model (keras.Model): Trained model.
        X_test (np.ndarray): Test images.
        y_test (np.ndarray): Test labels.

    Returns:
        dict: Evaluation results with keys "test_loss" and "test_accuracy".

    TODO:
        1. Call model.evaluate(X_test, y_test, verbose=0).
        2. Unpack result: loss, accuracy = model.evaluate(...)
        3. Print loss and accuracy in a user-friendly format.
        4. Return dict with keys "test_loss" and "test_accuracy".

    Example:
        metrics = evaluate_model(model, X_test, y_test)
        # -> {"test_loss": 0.1234, "test_accuracy": 0.9567}
    """
    # --- Write your evaluation code here ---

    return {}


def visualise_training(history):
    """
    Plot training loss and accuracy curves over epochs.

    Args:
        history (keras.callbacks.History): From model.fit().

    Returns:
        None (saves plots to disk).

    This function is already complete — study how it accesses
    history.history["loss"], history.history["accuracy"], etc.

    It demonstrates:
        - Tracking training progress over time
        - Identifying overfitting (train loss decreases, val loss increases)
    """
    if history is None:
        print("✗ No history to visualise (training failed?)")
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Plot loss
    axes[0].plot(history.history['loss'], label='Training Loss')
    axes[0].plot(history.history['val_loss'], label='Validation Loss')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Model Loss')
    axes[0].legend()
    axes[0].grid(True)

    # Plot accuracy
    axes[1].plot(history.history['accuracy'], label='Training Accuracy')
    axes[1].plot(history.history['val_accuracy'], label='Validation Accuracy')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Model Accuracy')
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig(METRICS_PATH)
    print(f"✓ Saved training metrics to {METRICS_PATH}")
    plt.close()


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict_image(model, image_path, class_names):
    """
    Classify a single image using the trained model.

    Args:
        model (keras.Model):      Trained classifier.
        image_path (str):         Path to image file.
        class_names (list[str]):  List of class names (in same order as training).

    Returns:
        dict: Prediction result with keys:
            "class":       Predicted class name.
            "confidence":  Probability (0.0–1.0).
            "all_probs":   Dict mapping class names to probabilities.

    TODO:
        1. Read the image from disk using cv2.imread(image_path).
           If image is None, raise FileNotFoundError.
        2. Resize to (IMAGE_HEIGHT, IMAGE_WIDTH).
        3. Normalise using preprocess_images() (expand dims first to get
           shape (1, H, W, C)):
           image = np.expand_dims(image, axis=0)
           image = preprocess_images(image)
        4. Get prediction: proba = model.predict(image, verbose=0)
           proba has shape (1, num_classes).
        5. Extract: proba = proba[0] (shape: (num_classes,))
        6. Get predicted class index: class_idx = np.argmax(proba)
        7. Get class name: class_name = class_names[class_idx]
        8. Get confidence: confidence = float(proba[class_idx])
        9. Build a dict mapping all class names to probabilities:
           all_probs = {name: float(prob) for name, prob in zip(class_names, proba)}
        10. Return dict with "class", "confidence", "all_probs".

    Example:
        result = predict_image(model, "cat.jpg", ["cats", "dogs"])
        # -> {"class": "cats", "confidence": 0.95, "all_probs": {...}}
    """
    # --- Write your prediction code here ---

    return {}


def save_model(model, filepath):
    """
    Save the trained model to disk for later use.

    Args:
        model (keras.Model): Trained model.
        filepath (str):      Where to save (usually ends in .h5 or .keras).

    Returns:
        None.

    This function is already complete.
    """
    model.save(filepath)
    print(f"✓ Model saved to {filepath}")


def load_model(filepath):
    """
    Load a previously trained model from disk.

    Args:
        filepath (str): Path to saved model.

    Returns:
        keras.Model: The loaded model, ready for prediction.

    This function is already complete.
    """
    model = keras.models.load_model(filepath)
    print(f"✓ Model loaded from {filepath}")
    return model


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main():
    """
    Orchestrate the full training and evaluation pipeline.

    This function is already complete — it shows how to wire all functions
    together. Just run:
        python image_classifier.py
    """
    print("\n" + "=" * 70)
    print("IMAGE CLASSIFICATION WITH DEEP LEARNING")
    print("=" * 70)

    # --- Check directories ---
    if not os.path.exists(TRAIN_DIR):
        print(f"\n✗ Error: {TRAIN_DIR} directory not found.")
        print("  Create directory structure:")
        print(f"    {TRAIN_DIR}/class1/image1.jpg")
        print(f"    {TRAIN_DIR}/class1/image2.jpg")
        print(f"    {TRAIN_DIR}/class2/image1.jpg")
        print(f"    ... etc")
        return

    # --- Step 1: Load training data ---
    print("\n[Step 1] Loading training images...")
    X_train, y_train, class_names = load_images(TRAIN_DIR)
    if len(X_train) == 0:
        print("  ✗ No training images found.")
        return
    print(f"  ✓ Loaded {len(X_train)} training images from {len(class_names)} classes")
    print(f"    Classes: {class_names}")

    # --- Step 2: Load test data ---
    print("\n[Step 2] Loading test images...")
    X_test, y_test, _ = load_images(TEST_DIR)
    if len(X_test) == 0:
        print("  ⚠ No test images found. Skipping evaluation.")
        X_test, y_test = None, None
    else:
        print(f"  ✓ Loaded {len(X_test)} test images")

    # --- Step 3: Preprocess images ---
    print("\n[Step 3] Preprocessing images...")
    X_train = preprocess_images(X_train)
    if X_test is not None:
        X_test = preprocess_images(X_test)
    print(f"  ✓ Normalised to [0, 1] range")

    # --- Step 4: Build model ---
    print("\n[Step 4] Building CNN model...")
    input_shape = (IMAGE_HEIGHT, IMAGE_WIDTH, CHANNELS)
    model = build_model(input_shape, len(class_names))
    if model is None:
        print("  ✗ build_model() returned None. Check your implementation.")
        return
    print(f"  ✓ Model created")
    print(f"    Input shape: {input_shape}")
    print(f"    Output classes: {len(class_names)}")

    # --- Step 5: Compile model ---
    print("\n[Step 5] Compiling model...")
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    print(f"  ✓ Model compiled")
    model.summary()

    # --- Step 6: Train model ---
    print("\n[Step 6] Training model...")
    history = train_model(model, X_train, y_train)
    if history is None:
        print("  ✗ train_model() returned None. Check your implementation.")
        return
    print(f"  ✓ Training complete")

    # --- Step 7: Evaluate model ---
    if X_test is not None:
        print("\n[Step 7] Evaluating on test set...")
        metrics = evaluate_model(model, X_test, y_test)
        if metrics:
            print(f"  Test Loss: {metrics['test_loss']:.4f}")
            print(f"  Test Accuracy: {metrics['test_accuracy']:.4%}")

    # --- Step 8: Visualise training ---
    print("\n[Step 8] Visualising training progress...")
    visualise_training(history)

    # --- Step 9: Save model ---
    print("\n[Step 9] Saving model...")
    save_model(model, MODEL_PATH)

    # --- Step 10: Test inference ---
    print("\n[Step 10] Testing inference on sample image...")
    sample_images = []
    for class_name in class_names:
        class_dir = os.path.join(TRAIN_DIR, class_name)
        if os.path.isdir(class_dir):
            files = os.listdir(class_dir)
            if files:
                sample_images.append(os.path.join(class_dir, files[0]))

    for image_path in sample_images[:2]:  # Test first 2 images
        try:
            result = predict_image(model, image_path, class_names)
            if result:
                print(f"  {image_path}")
                print(f"    → Predicted: {result['class']} ({result['confidence']:.2%} confidence)")
        except Exception as e:
            print(f"  ✗ Error predicting {image_path}: {e}")

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Directory structure example
# ---------------------------------------------------------------------------
#
# Create this structure before running:
#
# data/
#   train/
#     cats/
#       cat1.jpg
#       cat2.jpg
#       ... (50+ images)
#     dogs/
#       dog1.jpg
#       dog2.jpg
#       ... (50+ images)
#   test/
#     cats/
#       cat_test1.jpg
#       cat_test2.jpg
#       ... (10+ images)
#     dogs/
#       dog_test1.jpg
#       dog_test2.jpg
#       ... (10+ images)
#
# You can find open datasets at:
# - CIFAR-10: contains 60k 32×32 images (cars, cats, dogs, etc.)
# - ImageNet: contains millions of high-res images (large download)
# - Kaggle: many public image classification datasets
