"""
MLP CNN RCNN Ensemble
Keras-first handwritten-digit ensemble for Kaggle Digit Recognizer.

Owner: Patrick C O'Neil
Model: patrickoneil/mlp-cnn-rcnn-ensemble
Primary framework: Keras
Backend: TensorFlow
RCNN definition: Residual convolutional neural network

Run inside a Kaggle environment with the Digit Recognizer competition
data attached. The script trains, calibrates, evaluates, exports,
reloads, and validates the complete ensemble.
"""

# Cell 1 — Keras-first imports and stable TensorFlow runtime

import os

os.environ.setdefault("KERAS_BACKEND", "tensorflow")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import gc
import hashlib
import json
import math
import platform
import random
import shutil
import sys
import time
import warnings
import zipfile
from pathlib import Path

warnings.filterwarnings("ignore")

import joblib
import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import tensorflow as tf

from absl import logging as absl_logging
from IPython.display import display
from keras import layers
from sklearn.decomposition import PCA
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
)
from sklearn.model_selection import train_test_split

absl_logging.set_verbosity(absl_logging.ERROR)

tf.config.optimizer.set_experimental_options(
    {"layout_optimizer": False}
)
tf.config.optimizer.set_jit(False)

print("Python:", platform.python_version())
print("Keras:", keras.__version__)
print("Keras backend:", keras.backend.backend())
print("TensorFlow backend:", tf.__version__)
print("scikit-learn:", sklearn.__version__)
print("GPU devices:", tf.config.list_physical_devices("GPU"))
print(
    "TensorFlow optimizer options:",
    tf.config.optimizer.get_experimental_options(),
)

assert keras.backend.backend() == "tensorflow", (
    "This public Keras variation requires the TensorFlow backend."
)


# Cell 2 — Configuration, hardware detection, and reproducibility

OWNER = "Patrick C O'Neil"
MODEL_TITLE = "MLP CNN RCNN Ensemble"
MODEL_HANDLE = "patrickoneil/mlp-cnn-rcnn-ensemble"
MODEL_VARIATION_SLUG = "keras-digit-recognizer-ensemble"
PRIMARY_FRAMEWORK = "Keras"
RCNN_DEFINITION = "Residual convolutional neural network"

SEED = 42

RUN_MODE = os.environ.get(
    "DIGIT_ENSEMBLE_RUN_MODE",
    "full",
).strip().lower()

if RUN_MODE not in {"full", "smoke"}:
    raise ValueError("RUN_MODE must be either 'full' or 'smoke'.")

BATCH_SIZE = 128
MLP_BATCH_SIZE = 256
PREDICTION_BATCH_SIZE = 512

CNN_EPOCHS = 35
MLP_EPOCHS = 35

HARD_ROUNDS = 2
HARD_EPOCHS = 5
HARD_CONFIDENCE = 0.985
HARD_SAMPLE_WEIGHT = 4.0

PCA_COMPONENTS = 256

TEST_CONFIDENCE = 0.985
TEST_MARGIN = 0.20

TTA_SHIFTS = [
    (0, 0),
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]

RUN_FEATURE_IMPORTANCE = True
FEATURE_IMPORTANCE_SAMPLE_SIZE = 2000

if RUN_MODE == "smoke":
    CNN_EPOCHS = 1
    MLP_EPOCHS = 1
    HARD_ROUNDS = 1
    HARD_EPOCHS = 1
    PCA_COMPONENTS = 64
    FEATURE_IMPORTANCE_SAMPLE_SIZE = 128

OUTPUT_DIR = Path("/kaggle/working")

if not OUTPUT_DIR.exists():
    OUTPUT_DIR = Path("/mnt/data")

if not OUTPUT_DIR.exists():
    OUTPUT_DIR = Path.cwd()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_EXPORT_DIR = OUTPUT_DIR / "mlp-cnn-rcnn-ensemble"
MODEL_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

keras.utils.set_random_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)
tf.random.set_seed(SEED)

try:
    tf.config.experimental.enable_op_determinism()
    DETERMINISTIC_OPS = True
except Exception:
    DETERMINISTIC_OPS = False

gpu_devices = tf.config.list_physical_devices("GPU")
GPU_NAME = "CPU"
GPU_COMPUTE_CAPABILITY = None

if gpu_devices:
    gpu_details = tf.config.experimental.get_device_details(
        gpu_devices[0]
    )
    GPU_NAME = gpu_details.get(
        "device_name",
        gpu_devices[0].name,
    )
    GPU_COMPUTE_CAPABILITY = gpu_details.get(
        "compute_capability"
    )

# Stability-first policy for the Kaggle Tesla P100.
USE_MIXED_PRECISION = False
keras.mixed_precision.set_global_policy("float32")

print("Run mode:", RUN_MODE)
print("Output directory:", OUTPUT_DIR)
print("Model export directory:", MODEL_EXPORT_DIR)
print("GPU name:", GPU_NAME)
print("GPU compute capability:", GPU_COMPUTE_CAPABILITY)
print("Mixed precision enabled:", USE_MIXED_PRECISION)
print("Precision policy:", keras.mixed_precision.global_policy())
print("Deterministic operations:", DETERMINISTIC_OPS)

assert keras.mixed_precision.global_policy().name == "float32"


# Cell 3 — Locate the Kaggle Digit Recognizer files

def locate_competition_file(filename: str) -> Path:
    preferred_paths = [
        Path("/kaggle/input/digit-recognizer") / filename,
        Path("/kaggle/input/competitions/digit-recognizer") / filename,
        Path("/mnt/data") / filename,
        Path.cwd() / filename,
    ]

    for path in preferred_paths:
        if path.exists():
            return path.resolve()

    search_roots = [
        Path("/kaggle/input"),
        Path("/mnt/data"),
        Path.cwd(),
    ]

    matches = []

    for root in search_roots:
        if root.exists():
            matches.extend(root.rglob(filename))

    matches = [
        path.resolve()
        for path in matches
        if path.is_file()
    ]

    if not matches:
        checked = "\n".join(str(path) for path in preferred_paths)

        raise FileNotFoundError(
            f"Could not locate {filename}.\n"
            f"Checked these preferred paths:\n{checked}\n\n"
            "Attach the Kaggle Digit Recognizer competition data."
        )

    return sorted(
        matches,
        key=lambda path: (
            0 if "digit-recognizer" in str(path).lower() else 1,
            len(str(path)),
        ),
    )[0]


TRAIN_PATH = locate_competition_file("train.csv")
TEST_PATH = locate_competition_file("test.csv")

try:
    SAMPLE_SUBMISSION_PATH = locate_competition_file(
        "sample_submission.csv"
    )
except FileNotFoundError:
    SAMPLE_SUBMISSION_PATH = None

print("Training data:", TRAIN_PATH)
print("Testing data:", TEST_PATH)
print("Sample submission:", SAMPLE_SUBMISSION_PATH)

# Cell 4 — Load and validate the raw competition data

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

PIXEL_COLUMNS = [
    f"pixel{index}"
    for index in range(784)
]

expected_training_columns = ["label"] + PIXEL_COLUMNS
expected_testing_columns = PIXEL_COLUMNS

assert train_df.columns.tolist() == expected_training_columns, (
    "Training columns do not exactly match label + pixel0..pixel783."
)

assert test_df.columns.tolist() == expected_testing_columns, (
    "Testing columns do not exactly match pixel0..pixel783."
)

assert train_df.shape[1] == 785
assert test_df.shape[1] == 784
assert len(train_df) > 0
assert len(test_df) > 0

assert not train_df.isna().any().any(), (
    "Training data contains missing values."
)

assert not test_df.isna().any().any(), (
    "Testing data contains missing values."
)

train_pixel_min = float(
    train_df[PIXEL_COLUMNS].min().min()
)

train_pixel_max = float(
    train_df[PIXEL_COLUMNS].max().max()
)

test_pixel_min = float(
    test_df[PIXEL_COLUMNS].min().min()
)

test_pixel_max = float(
    test_df[PIXEL_COLUMNS].max().max()
)

assert 0.0 <= train_pixel_min <= train_pixel_max <= 255.0
assert 0.0 <= test_pixel_min <= test_pixel_max <= 255.0

observed_labels = sorted(
    train_df["label"].astype(int).unique().tolist()
)

assert observed_labels == list(range(10)), (
    f"Expected digit labels 0 through 9, found {observed_labels}."
)

print("Train shape:", train_df.shape)
print("Test shape:", test_df.shape)
print("Training pixel range:", train_pixel_min, "to", train_pixel_max)
print("Testing pixel range:", test_pixel_min, "to", test_pixel_max)
display(train_df.head())

# Cell 5 — Normalize and reshape images

y_all = train_df["label"].to_numpy(
    dtype=np.int64
)

x_all_flat = train_df[
    PIXEL_COLUMNS
].to_numpy(
    dtype=np.float32
)

x_test_flat = test_df[
    PIXEL_COLUMNS
].to_numpy(
    dtype=np.float32
)

x_all_flat /= 255.0
x_test_flat /= 255.0

x_all = x_all_flat.reshape(
    -1,
    28,
    28,
    1,
)

x_test = x_test_flat.reshape(
    -1,
    28,
    28,
    1,
)

assert x_all.shape == (
    len(train_df),
    28,
    28,
    1,
)

assert x_test.shape == (
    len(test_df),
    28,
    28,
    1,
)

assert x_all.dtype == np.float32
assert x_test.dtype == np.float32
assert np.isfinite(x_all).all()
assert np.isfinite(x_test).all()
assert 0.0 <= float(x_all.min()) <= float(x_all.max()) <= 1.0
assert 0.0 <= float(x_test.min()) <= float(x_test.max()) <= 1.0

label_counts = (
    pd.Series(y_all)
    .value_counts()
    .sort_index()
    .rename("Count")
    .to_frame()
)

print("x_all:", x_all.shape, x_all.dtype)
print("y_all:", y_all.shape, y_all.dtype)
print("x_test:", x_test.shape, x_test.dtype)
display(label_counts)

# Cell 6 — Optional smoke-test subset

if RUN_MODE == "smoke":
    smoke_train_limit = min(
        6000,
        len(x_all),
    )

    smoke_test_limit = min(
        1000,
        len(x_test),
    )

    smoke_indices, _ = train_test_split(
        np.arange(len(y_all)),
        train_size=smoke_train_limit,
        stratify=y_all,
        random_state=SEED,
    )

    x_all = x_all[smoke_indices]
    x_all_flat = x_all_flat[smoke_indices]
    y_all = y_all[smoke_indices]

    x_test = x_test[:smoke_test_limit]
    x_test_flat = x_test_flat[:smoke_test_limit]
    test_df = test_df.iloc[
        :smoke_test_limit
    ].reset_index(drop=True)

    print(
        "Smoke-test rows:",
        len(x_all),
        "training and",
        len(x_test),
        "testing",
    )
else:
    print("Full data retained.")

# Cell 7 — Create train, mining, blend, and untouched holdout partitions

all_indices = np.arange(
    len(y_all)
)

work_indices, holdout_indices = train_test_split(
    all_indices,
    test_size=0.05,
    stratify=y_all,
    random_state=SEED,
)

train_indices, temporary_indices = train_test_split(
    work_indices,
    test_size=15 / 95,
    stratify=y_all[work_indices],
    random_state=SEED,
)

mine_indices, blend_indices = train_test_split(
    temporary_indices,
    test_size=7 / 15,
    stratify=y_all[temporary_indices],
    random_state=SEED,
)

partition_indices = {
    "train": train_indices,
    "mine": mine_indices,
    "blend": blend_indices,
    "holdout": holdout_indices,
}

all_partition_indices = np.concatenate(
    list(partition_indices.values())
)

assert len(all_partition_indices) == len(y_all)
assert len(np.unique(all_partition_indices)) == len(y_all)
assert set(all_partition_indices.tolist()) == set(all_indices.tolist())

for left_name, left_values in partition_indices.items():
    for right_name, right_values in partition_indices.items():
        if left_name >= right_name:
            continue

        overlap = np.intersect1d(
            left_values,
            right_values,
        )

        assert len(overlap) == 0, (
            f"Data leakage: {left_name} overlaps {right_name}."
        )

x_train = x_all[train_indices]
y_train = y_all[train_indices]

x_mine = x_all[mine_indices]
y_mine = y_all[mine_indices]

x_blend = x_all[blend_indices]
y_blend = y_all[blend_indices]

x_holdout = x_all[holdout_indices]
y_holdout = y_all[holdout_indices]

partition_summary = pd.DataFrame(
    [
        {
            "Partition": name,
            "Rows": len(indices),
            "Percent": (
                100.0
                * len(indices)
                / len(y_all)
            ),
        }
        for name, indices in partition_indices.items()
    ]
)

display(partition_summary)

for name, features, labels in [
    ("train", x_train, y_train),
    ("mine", x_mine, y_mine),
    ("blend", x_blend, y_blend),
    ("holdout", x_holdout, y_holdout),
]:
    assert len(features) == len(labels)
    assert set(np.unique(labels).tolist()) == set(range(10))

    print(
        f"{name:8s}:",
        features.shape,
        labels.shape,
    )

# Cell 8 — Inspect representative training images

rng = np.random.default_rng(SEED)

image_count = min(
    15,
    len(x_train),
)

display_indices = rng.choice(
    len(x_train),
    size=image_count,
    replace=False,
)

rows = 3
columns = 5

fig, axes = plt.subplots(
    rows,
    columns,
    figsize=(10, 6),
)

for axis in axes.ravel():
    axis.axis("off")

for axis, index in zip(
    axes.ravel(),
    display_indices,
):
    axis.imshow(
        x_train[index, :, :, 0],
        cmap="gray",
    )

    axis.set_title(
        f"Label: {y_train[index]}"
    )

    axis.axis("off")

plt.tight_layout()
plt.show()

# Cell 9 — Stable optimizer, dataset, and residual-block helpers

def make_optimizer(
    learning_rate: float,
    weight_decay: float,
):
    try:
        return keras.optimizers.AdamW(
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            clipnorm=1.0,
        )
    except (AttributeError, TypeError):
        return keras.optimizers.Adam(
            learning_rate=learning_rate,
            clipnorm=1.0,
        )


def set_optimizer_learning_rate(
    optimizer,
    learning_rate: float,
) -> None:
    current_learning_rate = optimizer.learning_rate

    if hasattr(current_learning_rate, "assign"):
        current_learning_rate.assign(learning_rate)
    else:
        optimizer.learning_rate = learning_rate


def make_training_dataset(
    features: np.ndarray,
    labels: np.ndarray,
    batch_size: int,
    sample_weights: np.ndarray | None = None,
    shuffle: bool = True,
    seed: int = SEED,
) -> tf.data.Dataset:
    if len(features) != len(labels):
        raise ValueError(
            "Features and labels have different row counts."
        )

    if sample_weights is None:
        dataset = tf.data.Dataset.from_tensor_slices(
            (features, labels)
        )
    else:
        if len(sample_weights) != len(labels):
            raise ValueError(
                "Sample weights and labels have different row counts."
            )

        dataset = tf.data.Dataset.from_tensor_slices(
            (features, labels, sample_weights)
        )

    if shuffle:
        dataset = dataset.shuffle(
            buffer_size=min(len(labels), 10000),
            seed=seed,
            reshuffle_each_iteration=True,
        )

    dataset = dataset.batch(
        batch_size,
        drop_remainder=False,
    )

    options = tf.data.Options()
    options.deterministic = True
    options.threading.private_threadpool_size = 4
    options.threading.max_intra_op_parallelism = 1

    dataset = dataset.with_options(options)
    dataset = dataset.prefetch(1)

    return dataset


def residual_block(
    inputs,
    filters: int,
    stride: int = 1,
    dropout: float = 0.0,
):
    shortcut = inputs

    x = layers.Conv2D(
        filters=filters,
        kernel_size=3,
        strides=stride,
        padding="same",
        use_bias=False,
        kernel_initializer="he_normal",
    )(inputs)

    x = layers.BatchNormalization()(x)
    x = layers.Activation("swish")(x)

    x = layers.Conv2D(
        filters=filters,
        kernel_size=3,
        strides=1,
        padding="same",
        use_bias=False,
        kernel_initializer="he_normal",
    )(x)

    x = layers.BatchNormalization()(x)

    shortcut_channels = shortcut.shape[-1]

    needs_projection = (
        stride != 1
        or shortcut_channels is None
        or int(shortcut_channels) != filters
    )

    if needs_projection:
        shortcut = layers.Conv2D(
            filters=filters,
            kernel_size=1,
            strides=stride,
            padding="same",
            use_bias=False,
            kernel_initializer="he_normal",
        )(shortcut)

        shortcut = layers.BatchNormalization()(shortcut)

    x = layers.Add()([x, shortcut])
    x = layers.Activation("swish")(x)

    if dropout > 0:
        x = layers.Dropout(rate=dropout)(x)

    return x


# Cell 10 — Build the stable Keras residual CNN branch

def build_residual_cnn() -> keras.Model:
    augmentation = keras.Sequential(
        [
            layers.RandomTranslation(
                height_factor=0.08,
                width_factor=0.08,
                fill_mode="constant",
                seed=SEED + 1,
            ),
            layers.RandomRotation(
                factor=0.06,
                fill_mode="constant",
                seed=SEED + 2,
            ),
            layers.RandomZoom(
                height_factor=0.08,
                width_factor=0.08,
                fill_mode="constant",
                seed=SEED + 3,
            ),
        ],
        name="augmentation",
    )

    inputs = keras.Input(
        shape=(28, 28, 1),
        dtype="float32",
        name="image",
    )

    x = augmentation(inputs)

    x = layers.Conv2D(
        filters=32,
        kernel_size=3,
        padding="same",
        use_bias=False,
        kernel_initializer="he_normal",
        name="stem_conv",
    )(x)

    x = layers.BatchNormalization(
        name="stem_batch_norm"
    )(x)

    x = layers.Activation(
        "swish",
        name="stem_activation",
    )(x)

    x = residual_block(
        x,
        filters=32,
        dropout=0.04,
    )

    x = residual_block(
        x,
        filters=64,
        stride=2,
        dropout=0.07,
    )

    x = residual_block(
        x,
        filters=64,
        dropout=0.07,
    )

    x = residual_block(
        x,
        filters=128,
        stride=2,
        dropout=0.10,
    )

    x = residual_block(
        x,
        filters=128,
        dropout=0.10,
    )

    x = layers.Conv2D(
        filters=192,
        kernel_size=3,
        padding="same",
        activation="swish",
        dtype="float32",
        name="final_conv",
    )(x)

    x = layers.GlobalAveragePooling2D(
        name="global_average_pool"
    )(x)

    x = layers.Dense(
        units=192,
        activation="swish",
        dtype="float32",
        name="dense_192",
    )(x)

    x = layers.Dropout(
        rate=0.25,
        name="head_dropout",
    )(x)

    logits = layers.Dense(
        units=10,
        dtype="float32",
        name="logits",
    )(x)

    model = keras.Model(
        inputs=inputs,
        outputs=logits,
        name="residual_cnn",
    )

    model.compile(
        optimizer=make_optimizer(
            learning_rate=1e-3,
            weight_decay=1e-4,
        ),
        loss=keras.losses.SparseCategoricalCrossentropy(
            from_logits=True
        ),
        metrics=[
            keras.metrics.SparseCategoricalAccuracy(
                name="accuracy"
            )
        ],
        run_eagerly=False,
        jit_compile=False,
    )

    return model


keras.backend.clear_session()

cnn = build_residual_cnn()
cnn.summary()

assert cnn.input_shape == (
    None,
    28,
    28,
    1,
)

assert cnn.output_shape == (
    None,
    10,
)

print(
    "CNN compiled with float32 policy, "
    "layout optimization disabled, "
    "and JIT compilation disabled."
)


# Cell 11 — Validate the CNN before training

cnn_test_logits = cnn(
    x_train[: min(8, len(x_train))],
    training=False,
)

cnn_test_logits = np.asarray(
    cnn_test_logits,
    dtype=np.float32,
)

assert cnn.input_shape == (
    None,
    28,
    28,
    1,
)

assert cnn.output_shape == (
    None,
    10,
)

assert cnn_test_logits.shape == (
    min(8, len(x_train)),
    10,
)

assert np.isfinite(cnn_test_logits).all()
assert cnn.count_params() > 0

CNN_PARAMETER_COUNT = int(
    cnn.count_params()
)

print("CNN parameters:", f"{CNN_PARAMETER_COUNT:,}")
print("CNN forward-pass shape:", cnn_test_logits.shape)

# Cell 12 — Train the residual CNN with an explicit tf.data pipeline

CNN_CHECKPOINT_PATH = (
    MODEL_EXPORT_DIR
    / "best_residual_cnn.keras"
)

if CNN_CHECKPOINT_PATH.exists():
    CNN_CHECKPOINT_PATH.unlink()

cnn_callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath=CNN_CHECKPOINT_PATH,
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        verbose=1,
    ),
    keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        mode="max",
        patience=7,
        restore_best_weights=True,
        verbose=1,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        mode="min",
        factor=0.35,
        patience=2,
        min_lr=1e-6,
        verbose=1,
    ),
    keras.callbacks.TerminateOnNaN(),
]

cnn_train_dataset = make_training_dataset(
    features=x_train,
    labels=y_train,
    batch_size=BATCH_SIZE,
    sample_weights=None,
    shuffle=True,
    seed=SEED,
)

cnn_blend_dataset = make_training_dataset(
    features=x_blend,
    labels=y_blend,
    batch_size=BATCH_SIZE,
    sample_weights=None,
    shuffle=False,
    seed=SEED,
)

cnn_training_started = time.perf_counter()

cnn_history = cnn.fit(
    cnn_train_dataset,
    validation_data=cnn_blend_dataset,
    epochs=CNN_EPOCHS,
    callbacks=cnn_callbacks,
    verbose=2,
)

CNN_TRAINING_SECONDS = float(
    time.perf_counter()
    - cnn_training_started
)

if not CNN_CHECKPOINT_PATH.exists():
    raise FileNotFoundError(
        "The CNN checkpoint was not created."
    )

if CNN_CHECKPOINT_PATH.stat().st_size <= 0:
    raise RuntimeError(
        "The CNN checkpoint is empty."
    )

cnn = keras.models.load_model(
    CNN_CHECKPOINT_PATH,
    compile=True,
)

final_validation_accuracy = float(
    max(cnn_history.history["val_accuracy"])
)

assert np.isfinite(final_validation_accuracy)

print(
    "Best CNN blend accuracy:",
    f"{final_validation_accuracy:.6f}",
)

print(
    "CNN training seconds:",
    f"{CNN_TRAINING_SECONDS:,.2f}",
)

print(
    "CNN checkpoint:",
    CNN_CHECKPOINT_PATH,
)


# Cell 13 — Plot and save CNN training history

cnn_history_df = pd.DataFrame(
    cnn_history.history
)

CNN_HISTORY_PATH = (
    MODEL_EXPORT_DIR
    / "training_history_cnn.csv"
)

cnn_history_df.to_csv(
    CNN_HISTORY_PATH,
    index=False,
)

assert not cnn_history_df.empty
assert "loss" in cnn_history_df.columns
assert "accuracy" in cnn_history_df.columns

fig, axis = plt.subplots(
    figsize=(8, 4)
)

axis.plot(
    cnn_history_df["accuracy"],
    label="training accuracy",
)

axis.plot(
    cnn_history_df["val_accuracy"],
    label="blend accuracy",
)

axis.set_xlabel("Epoch")
axis.set_ylabel("Accuracy")
axis.set_title("Residual CNN Accuracy")
axis.legend()

plt.tight_layout()
plt.show()

fig, axis = plt.subplots(
    figsize=(8, 4)
)

axis.plot(
    cnn_history_df["loss"],
    label="training loss",
)

axis.plot(
    cnn_history_df["val_loss"],
    label="blend loss",
)

axis.set_xlabel("Epoch")
axis.set_ylabel("Loss")
axis.set_title("Residual CNN Loss")
axis.legend()

plt.tight_layout()
plt.show()

# Cell 14 — Probability and validation helpers

def stable_softmax(
    logits: np.ndarray,
    temperature: float = 1.0,
) -> np.ndarray:
    logits = np.asarray(
        logits,
        dtype=np.float64,
    )

    temperature = float(
        temperature
    )

    if not np.isfinite(temperature):
        raise ValueError(
            "Temperature must be finite."
        )

    if temperature <= 0:
        raise ValueError(
            "Temperature must be greater than zero."
        )

    scaled = logits / temperature
    scaled -= scaled.max(
        axis=1,
        keepdims=True,
    )

    exponentials = np.exp(scaled)

    probabilities = exponentials / exponentials.sum(
        axis=1,
        keepdims=True,
    )

    return probabilities.astype(
        np.float32
    )


def validate_probabilities(
    probabilities: np.ndarray,
    expected_rows: int,
    name: str,
) -> None:
    probabilities = np.asarray(
        probabilities
    )

    assert probabilities.shape == (
        expected_rows,
        10,
    ), (
        f"{name} shape is {probabilities.shape}, "
        f"expected {(expected_rows, 10)}."
    )

    assert np.isfinite(
        probabilities
    ).all(), (
        f"{name} contains NaN or infinite values."
    )

    assert float(probabilities.min()) >= -1e-7
    assert float(probabilities.max()) <= 1.0 + 1e-7

    row_sums = probabilities.sum(
        axis=1
    )

    assert np.allclose(
        row_sums,
        1.0,
        atol=1e-5,
    ), (
        f"{name} rows do not sum to one."
    )


def predict_logits(
    model: keras.Model,
    features: np.ndarray,
    batch_size: int = PREDICTION_BATCH_SIZE,
    verbose: int = 0,
) -> np.ndarray:
    logits = model.predict(
        features,
        batch_size=batch_size,
        verbose=verbose,
    )

    logits = np.asarray(
        logits,
        dtype=np.float32,
    )

    assert logits.shape == (
        len(features),
        10,
    )

    assert np.isfinite(logits).all()

    return logits


def predict_probabilities(
    model: keras.Model,
    features: np.ndarray,
    temperature: float = 1.0,
    batch_size: int = PREDICTION_BATCH_SIZE,
    verbose: int = 0,
) -> np.ndarray:
    logits = predict_logits(
        model=model,
        features=features,
        batch_size=batch_size,
        verbose=verbose,
    )

    probabilities = stable_softmax(
        logits,
        temperature=temperature,
    )

    validate_probabilities(
        probabilities,
        expected_rows=len(features),
        name=f"{model.name} probabilities",
    )

    return probabilities

# Cell 15 — Supervised hard-example mining for the CNN

baseline_blend_probabilities = (
    predict_probabilities(
        model=cnn,
        features=x_blend,
    )
)

best_feedback_accuracy = float(
    accuracy_score(
        y_blend,
        baseline_blend_probabilities.argmax(
            axis=1
        ),
    )
)

hard_mining_records = []

for round_number in range(
    1,
    HARD_ROUNDS + 1,
):
    mining_probabilities = (
        predict_probabilities(
            model=cnn,
            features=x_mine,
        )
    )

    mining_predictions = (
        mining_probabilities.argmax(
            axis=1
        )
    )

    mining_confidence = (
        mining_probabilities.max(
            axis=1
        )
    )

    hard_mask = (
        (
            mining_predictions
            != y_mine
        )
        | (
            mining_confidence
            < HARD_CONFIDENCE
        )
    )

    hard_x = x_mine[hard_mask]
    hard_y = y_mine[hard_mask]
    hard_count = int(len(hard_y))

    print(
        f"Hard-example round {round_number}: "
        f"{hard_count:,}/{len(y_mine):,}"
    )

    if hard_count == 0:
        hard_mining_records.append(
            {
                "Round": round_number,
                "HardExamples": 0,
                "BlendAccuracy": (
                    best_feedback_accuracy
                ),
                "Accepted": False,
            }
        )

        break

    feedback_x = np.concatenate(
        [
            x_train,
            hard_x,
        ],
        axis=0,
    )

    feedback_y = np.concatenate(
        [
            y_train,
            hard_y,
        ],
        axis=0,
    )

    feedback_weights = np.concatenate(
        [
            np.ones(
                len(y_train),
                dtype=np.float32,
            ),
            np.full(
                hard_count,
                HARD_SAMPLE_WEIGHT,
                dtype=np.float32,
            ),
        ]
    )

    feedback_order = (
        np.random.default_rng(
            SEED + round_number
        )
        .permutation(
            len(feedback_y)
        )
    )

    set_optimizer_learning_rate(
        cnn.optimizer,
        2e-4,
    )

    feedback_dataset = make_training_dataset(
        features=feedback_x[feedback_order],
        labels=feedback_y[feedback_order],
        sample_weights=feedback_weights[
            feedback_order
        ],
        batch_size=BATCH_SIZE,
        shuffle=False,
        seed=SEED + round_number,
    )

    feedback_blend_dataset = make_training_dataset(
        features=x_blend,
        labels=y_blend,
        sample_weights=None,
        batch_size=BATCH_SIZE,
        shuffle=False,
        seed=SEED,
    )

    cnn.fit(
        feedback_dataset,
        validation_data=feedback_blend_dataset,
        epochs=HARD_EPOCHS,
        callbacks=[
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.40,
                patience=1,
                min_lr=5e-7,
                verbose=1,
            ),
            keras.callbacks.TerminateOnNaN(),
        ],
        verbose=2,
    )

    current_blend_probabilities = (
        predict_probabilities(
            model=cnn,
            features=x_blend,
        )
    )

    current_blend_accuracy = float(
        accuracy_score(
            y_blend,
            current_blend_probabilities.argmax(
                axis=1
            ),
        )
    )

    accepted = (
        current_blend_accuracy
        >= best_feedback_accuracy
    )

    hard_mining_records.append(
        {
            "Round": round_number,
            "HardExamples": hard_count,
            "BlendAccuracy": (
                current_blend_accuracy
            ),
            "Accepted": bool(accepted),
        }
    )

    print(
        "Blend accuracy after feedback:",
        f"{current_blend_accuracy:.6f}",
    )

    if accepted:
        best_feedback_accuracy = (
            current_blend_accuracy
        )

        cnn.save(
            CNN_CHECKPOINT_PATH
        )
    else:
        print(
            "Feedback did not improve the blend set; "
            "restoring the previous best CNN."
        )

        cnn = keras.models.load_model(
            CNN_CHECKPOINT_PATH
        )

        break

hard_mining_df = pd.DataFrame(
    hard_mining_records
)

HARD_MINING_PATH = (
    MODEL_EXPORT_DIR
    / "hard_example_mining.csv"
)

hard_mining_df.to_csv(
    HARD_MINING_PATH,
    index=False,
)

display(hard_mining_df)

# Cell 16 — Fit the whitened PCA transformation

x_reduce = np.concatenate(
    [
        x_train,
        x_mine,
    ],
    axis=0,
).reshape(
    -1,
    784,
)

y_reduce = np.concatenate(
    [
        y_train,
        y_mine,
    ],
    axis=0,
)

effective_pca_components = min(
    PCA_COMPONENTS,
    x_reduce.shape[0] - 1,
    x_reduce.shape[1],
)

assert effective_pca_components >= 10

pca = PCA(
    n_components=effective_pca_components,
    whiten=True,
    svd_solver="randomized",
    random_state=SEED,
)

pca_started = time.perf_counter()

z_train = pca.fit_transform(
    x_reduce
).astype(
    np.float32
)

PCA_TRAINING_SECONDS = float(
    time.perf_counter()
    - pca_started
)

z_blend = pca.transform(
    x_blend.reshape(-1, 784)
).astype(
    np.float32
)

z_holdout = pca.transform(
    x_holdout.reshape(-1, 784)
).astype(
    np.float32
)

z_test = pca.transform(
    x_test.reshape(-1, 784)
).astype(
    np.float32
)

for name, transformed, expected_rows in [
    ("z_train", z_train, len(x_reduce)),
    ("z_blend", z_blend, len(x_blend)),
    ("z_holdout", z_holdout, len(x_holdout)),
    ("z_test", z_test, len(x_test)),
]:
    assert transformed.shape == (
        expected_rows,
        effective_pca_components,
    )

    assert transformed.dtype == np.float32
    assert np.isfinite(transformed).all()

assert pca.whiten is True
assert pca.n_components_ == effective_pca_components

PCA_EXPLAINED_VARIANCE = float(
    pca.explained_variance_ratio_.sum()
)

print(
    "PCA components:",
    effective_pca_components,
)

print(
    "PCA explained variance:",
    f"{PCA_EXPLAINED_VARIANCE:.4%}",
)

print(
    "PCA fit seconds:",
    f"{PCA_TRAINING_SECONDS:,.2f}",
)

# Cell 17 — Build the Keras PCA-MLP branch

def build_pca_mlp(
    number_of_features: int,
) -> keras.Model:
    inputs = keras.Input(
        shape=(
            number_of_features,
        ),
        name="pca_features",
    )

    x = layers.BatchNormalization(
        name="input_batch_norm"
    )(inputs)

    x = layers.Dense(
        768,
        activation="swish",
        name="dense_768",
    )(x)

    x = layers.BatchNormalization(
        name="batch_norm_768"
    )(x)

    x = layers.Dropout(
        0.30,
        name="dropout_768",
    )(x)

    x = layers.Dense(
        384,
        activation="swish",
        name="dense_384",
    )(x)

    x = layers.BatchNormalization(
        name="batch_norm_384"
    )(x)

    x = layers.Dropout(
        0.25,
        name="dropout_384",
    )(x)

    x = layers.Dense(
        160,
        activation="swish",
        name="dense_160",
    )(x)

    x = layers.Dropout(
        0.15,
        name="dropout_160",
    )(x)

    logits = layers.Dense(
        10,
        dtype="float32",
        name="logits",
    )(x)

    model = keras.Model(
        inputs=inputs,
        outputs=logits,
        name="pca_mlp",
    )

    model.compile(
        optimizer=make_optimizer(
            learning_rate=8e-4,
            weight_decay=2e-4,
        ),
        loss=keras.losses.SparseCategoricalCrossentropy(
            from_logits=True
        ),
        metrics=[
            keras.metrics.SparseCategoricalAccuracy(
                name="accuracy"
            )
        ],
    )

    return model


mlp = build_pca_mlp(
    effective_pca_components
)

mlp.summary()

mlp_test_logits = mlp(
    z_train[: min(8, len(z_train))],
    training=False,
)

mlp_test_logits = np.asarray(
    mlp_test_logits,
    dtype=np.float32,
)

assert mlp.input_shape == (
    None,
    effective_pca_components,
)

assert mlp.output_shape == (
    None,
    10,
)

assert mlp_test_logits.shape == (
    min(8, len(z_train)),
    10,
)

assert np.isfinite(mlp_test_logits).all()

MLP_PARAMETER_COUNT = int(
    mlp.count_params()
)

print("MLP parameters:", f"{MLP_PARAMETER_COUNT:,}")

# Cell 18 — Train the PCA-MLP

MLP_CHECKPOINT_PATH = (
    MODEL_EXPORT_DIR
    / "best_pca_mlp.keras"
)

mlp_callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath=MLP_CHECKPOINT_PATH,
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        verbose=1,
    ),
    keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        mode="max",
        patience=7,
        restore_best_weights=True,
        verbose=1,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        mode="min",
        factor=0.35,
        patience=2,
        min_lr=1e-6,
        verbose=1,
    ),
    keras.callbacks.TerminateOnNaN(),
]

mlp_training_started = time.perf_counter()

mlp_history = mlp.fit(
    z_train,
    y_reduce,
    validation_data=(
        z_blend,
        y_blend,
    ),
    epochs=MLP_EPOCHS,
    batch_size=MLP_BATCH_SIZE,
    callbacks=mlp_callbacks,
    verbose=2,
)

MLP_TRAINING_SECONDS = float(
    time.perf_counter()
    - mlp_training_started
)

assert MLP_CHECKPOINT_PATH.exists()
assert MLP_CHECKPOINT_PATH.stat().st_size > 0

mlp = keras.models.load_model(
    MLP_CHECKPOINT_PATH
)

print(
    "MLP training seconds:",
    f"{MLP_TRAINING_SECONDS:,.2f}",
)

# Cell 19 — Plot and save MLP training history

mlp_history_df = pd.DataFrame(
    mlp_history.history
)

MLP_HISTORY_PATH = (
    MODEL_EXPORT_DIR
    / "training_history_mlp.csv"
)

mlp_history_df.to_csv(
    MLP_HISTORY_PATH,
    index=False,
)

assert not mlp_history_df.empty
assert "loss" in mlp_history_df.columns
assert "accuracy" in mlp_history_df.columns

fig, axis = plt.subplots(
    figsize=(8, 4)
)

axis.plot(
    mlp_history_df["accuracy"],
    label="training accuracy",
)

axis.plot(
    mlp_history_df["val_accuracy"],
    label="blend accuracy",
)

axis.set_xlabel("Epoch")
axis.set_ylabel("Accuracy")
axis.set_title("PCA-MLP Accuracy")
axis.legend()

plt.tight_layout()
plt.show()

fig, axis = plt.subplots(
    figsize=(8, 4)
)

axis.plot(
    mlp_history_df["loss"],
    label="training loss",
)

axis.plot(
    mlp_history_df["val_loss"],
    label="blend loss",
)

axis.set_xlabel("Epoch")
axis.set_ylabel("Loss")
axis.set_title("PCA-MLP Loss")
axis.legend()

plt.tight_layout()
plt.show()

# Cell 20 — Temperature calibration for each branch

TEMPERATURE_GRID = np.linspace(
    0.60,
    2.00,
    71,
)

def find_best_temperature(
    logits: np.ndarray,
    labels: np.ndarray,
) -> tuple[float, float]:
    best_temperature = 1.0
    best_loss = math.inf

    for temperature in TEMPERATURE_GRID:
        probabilities = stable_softmax(
            logits,
            temperature=float(
                temperature
            ),
        )

        current_loss = float(
            log_loss(
                labels,
                probabilities,
                labels=np.arange(10),
            )
        )

        if current_loss < best_loss:
            best_temperature = float(
                temperature
            )

            best_loss = (
                current_loss
            )

    return (
        best_temperature,
        best_loss,
    )


cnn_blend_logits = predict_logits(
    model=cnn,
    features=x_blend,
)

mlp_blend_logits = predict_logits(
    model=mlp,
    features=z_blend,
)

cnn_temperature, cnn_calibrated_loss = (
    find_best_temperature(
        cnn_blend_logits,
        y_blend,
    )
)

mlp_temperature, mlp_calibrated_loss = (
    find_best_temperature(
        mlp_blend_logits,
        y_blend,
    )
)

cnn_blend_prob = stable_softmax(
    cnn_blend_logits,
    temperature=cnn_temperature,
)

mlp_blend_prob = stable_softmax(
    mlp_blend_logits,
    temperature=mlp_temperature,
)

validate_probabilities(
    cnn_blend_prob,
    expected_rows=len(y_blend),
    name="Calibrated CNN blend probabilities",
)

validate_probabilities(
    mlp_blend_prob,
    expected_rows=len(y_blend),
    name="Calibrated MLP blend probabilities",
)

print(
    "CNN temperature:",
    f"{cnn_temperature:.3f}",
    "log loss:",
    f"{cnn_calibrated_loss:.6f}",
)

print(
    "MLP temperature:",
    f"{mlp_temperature:.3f}",
    "log loss:",
    f"{mlp_calibrated_loss:.6f}",
)

# Cell 21 — Select the weighted ensemble on the blend partition

cnn_blend_accuracy = float(
    accuracy_score(
        y_blend,
        cnn_blend_prob.argmax(
            axis=1
        ),
    )
)

mlp_blend_accuracy = float(
    accuracy_score(
        y_blend,
        mlp_blend_prob.argmax(
            axis=1
        ),
    )
)

ENSEMBLE_WEIGHT_GRID = np.linspace(
    0.65,
    1.00,
    71,
)

best_cnn_weight = 1.0
best_ensemble_accuracy = -1.0
best_ensemble_loss = math.inf

ensemble_search_records = []

for cnn_weight in ENSEMBLE_WEIGHT_GRID:
    cnn_weight = float(
        cnn_weight
    )

    mlp_weight = (
        1.0
        - cnn_weight
    )

    ensemble_probability = (
        cnn_weight
        * cnn_blend_prob
        + mlp_weight
        * mlp_blend_prob
    )

    validate_probabilities(
        ensemble_probability,
        expected_rows=len(y_blend),
        name="Blend ensemble probabilities",
    )

    current_accuracy = float(
        accuracy_score(
            y_blend,
            ensemble_probability.argmax(
                axis=1
            ),
        )
    )

    current_loss = float(
        log_loss(
            y_blend,
            ensemble_probability,
            labels=np.arange(10),
        )
    )

    ensemble_search_records.append(
        {
            "CNNWeight": cnn_weight,
            "MLPWeight": mlp_weight,
            "Accuracy": current_accuracy,
            "LogLoss": current_loss,
        }
    )

    improved_accuracy = (
        current_accuracy
        > best_ensemble_accuracy
    )

    tied_accuracy = np.isclose(
        current_accuracy,
        best_ensemble_accuracy,
        atol=1e-12,
    )

    tied_with_better_loss = (
        tied_accuracy
        and current_loss
        < best_ensemble_loss
    )

    if (
        improved_accuracy
        or tied_with_better_loss
    ):
        best_cnn_weight = (
            cnn_weight
        )

        best_ensemble_accuracy = (
            current_accuracy
        )

        best_ensemble_loss = (
            current_loss
        )

best_mlp_weight = (
    1.0
    - best_cnn_weight
)

ensemble_search_df = pd.DataFrame(
    ensemble_search_records
)

ENSEMBLE_SEARCH_PATH = (
    MODEL_EXPORT_DIR
    / "ensemble_weight_search.csv"
)

ensemble_search_df.to_csv(
    ENSEMBLE_SEARCH_PATH,
    index=False,
)

assert 0.0 <= best_cnn_weight <= 1.0
assert 0.0 <= best_mlp_weight <= 1.0
assert np.isclose(
    best_cnn_weight + best_mlp_weight,
    1.0,
)

print(
    "CNN blend accuracy:",
    f"{cnn_blend_accuracy:.6f}",
)

print(
    "MLP blend accuracy:",
    f"{mlp_blend_accuracy:.6f}",
)

print(
    "Selected CNN weight:",
    f"{best_cnn_weight:.3f}",
)

print(
    "Selected MLP weight:",
    f"{best_mlp_weight:.3f}",
)

print(
    "Selected blend accuracy:",
    f"{best_ensemble_accuracy:.6f}",
)

print(
    "Selected blend log loss:",
    f"{best_ensemble_loss:.6f}",
)

# Cell 22 — Evaluate on the untouched holdout

def expected_calibration_error(
    labels: np.ndarray,
    probabilities: np.ndarray,
    number_of_bins: int = 15,
) -> float:
    confidence = probabilities.max(
        axis=1
    )

    predictions = probabilities.argmax(
        axis=1
    )

    correctness = (
        predictions
        == labels
    ).astype(
        np.float64
    )

    bin_edges = np.linspace(
        0.0,
        1.0,
        number_of_bins + 1,
    )

    ece = 0.0

    for bin_index in range(
        number_of_bins
    ):
        lower = bin_edges[
            bin_index
        ]

        upper = bin_edges[
            bin_index + 1
        ]

        if bin_index == 0:
            in_bin = (
                confidence >= lower
            ) & (
                confidence <= upper
            )
        else:
            in_bin = (
                confidence > lower
            ) & (
                confidence <= upper
            )

        if not in_bin.any():
            continue

        bin_accuracy = correctness[
            in_bin
        ].mean()

        bin_confidence = confidence[
            in_bin
        ].mean()

        bin_weight = in_bin.mean()

        ece += (
            bin_weight
            * abs(
                bin_accuracy
                - bin_confidence
            )
        )

    return float(ece)


cnn_holdout_logits = predict_logits(
    model=cnn,
    features=x_holdout,
)

mlp_holdout_logits = predict_logits(
    model=mlp,
    features=z_holdout,
)

cnn_holdout_prob = stable_softmax(
    cnn_holdout_logits,
    temperature=cnn_temperature,
)

mlp_holdout_prob = stable_softmax(
    mlp_holdout_logits,
    temperature=mlp_temperature,
)

holdout_ensemble_prob = (
    best_cnn_weight
    * cnn_holdout_prob
    + best_mlp_weight
    * mlp_holdout_prob
)

validate_probabilities(
    cnn_holdout_prob,
    expected_rows=len(y_holdout),
    name="CNN holdout probabilities",
)

validate_probabilities(
    mlp_holdout_prob,
    expected_rows=len(y_holdout),
    name="MLP holdout probabilities",
)

validate_probabilities(
    holdout_ensemble_prob,
    expected_rows=len(y_holdout),
    name="Ensemble holdout probabilities",
)

cnn_holdout_prediction = (
    cnn_holdout_prob.argmax(
        axis=1
    )
)

mlp_holdout_prediction = (
    mlp_holdout_prob.argmax(
        axis=1
    )
)

ensemble_holdout_prediction = (
    holdout_ensemble_prob.argmax(
        axis=1
    )
)

cnn_holdout_accuracy = float(
    accuracy_score(
        y_holdout,
        cnn_holdout_prediction,
    )
)

mlp_holdout_accuracy = float(
    accuracy_score(
        y_holdout,
        mlp_holdout_prediction,
    )
)

ensemble_holdout_accuracy = float(
    accuracy_score(
        y_holdout,
        ensemble_holdout_prediction,
    )
)

cnn_holdout_log_loss = float(
    log_loss(
        y_holdout,
        cnn_holdout_prob,
        labels=np.arange(10),
    )
)

mlp_holdout_log_loss = float(
    log_loss(
        y_holdout,
        mlp_holdout_prob,
        labels=np.arange(10),
    )
)

ensemble_holdout_log_loss = float(
    log_loss(
        y_holdout,
        holdout_ensemble_prob,
        labels=np.arange(10),
    )
)

ensemble_holdout_ece = (
    expected_calibration_error(
        y_holdout,
        holdout_ensemble_prob,
    )
)

print(
    "CNN holdout accuracy:",
    f"{cnn_holdout_accuracy:.6f}",
)

print(
    "MLP holdout accuracy:",
    f"{mlp_holdout_accuracy:.6f}",
)

print(
    "Ensemble holdout accuracy:",
    f"{ensemble_holdout_accuracy:.6f}",
)

print(
    "Ensemble holdout log loss:",
    f"{ensemble_holdout_log_loss:.6f}",
)

print(
    "Ensemble holdout ECE:",
    f"{ensemble_holdout_ece:.6f}",
)

# Cell 23 — Per-class evaluation and confusion matrix

holdout_confusion_matrix = (
    confusion_matrix(
        y_holdout,
        ensemble_holdout_prediction,
        labels=np.arange(10),
    )
)

holdout_classification_report = (
    classification_report(
        y_holdout,
        ensemble_holdout_prediction,
        labels=np.arange(10),
        output_dict=True,
        zero_division=0,
    )
)

classification_report_df = (
    pd.DataFrame(
        holdout_classification_report
    )
    .transpose()
    .reset_index()
    .rename(
        columns={
            "index": "ClassOrAverage"
        }
    )
)

confusion_matrix_df = pd.DataFrame(
    holdout_confusion_matrix,
    index=[
        f"actual_{digit}"
        for digit in range(10)
    ],
    columns=[
        f"predicted_{digit}"
        for digit in range(10)
    ],
)

CLASSIFICATION_REPORT_PATH = (
    MODEL_EXPORT_DIR
    / "classification_report.csv"
)

CONFUSION_MATRIX_PATH = (
    MODEL_EXPORT_DIR
    / "confusion_matrix.csv"
)

classification_report_df.to_csv(
    CLASSIFICATION_REPORT_PATH,
    index=False,
)

confusion_matrix_df.to_csv(
    CONFUSION_MATRIX_PATH
)

display(classification_report_df)
display(confusion_matrix_df)

fig, axis = plt.subplots(
    figsize=(8, 7)
)

image = axis.imshow(
    holdout_confusion_matrix,
    cmap="Blues",
)

axis.set_title(
    "Untouched Holdout Confusion Matrix"
)

axis.set_xlabel(
    "Predicted digit"
)

axis.set_ylabel(
    "Actual digit"
)

axis.set_xticks(
    np.arange(10)
)

axis.set_yticks(
    np.arange(10)
)

for actual_digit in range(10):
    for predicted_digit in range(10):
        value = int(
            holdout_confusion_matrix[
                actual_digit,
                predicted_digit,
            ]
        )

        axis.text(
            predicted_digit,
            actual_digit,
            str(value),
            ha="center",
            va="center",
            fontsize=8,
        )

fig.colorbar(
    image,
    ax=axis,
)

plt.tight_layout()
plt.show()

# Cell 24 — Predict the competition test data

test_prediction_started = (
    time.perf_counter()
)

cnn_test_logits = predict_logits(
    model=cnn,
    features=x_test,
    verbose=1,
)

mlp_test_logits = predict_logits(
    model=mlp,
    features=z_test,
    verbose=1,
)

cnn_test_prob = stable_softmax(
    cnn_test_logits,
    temperature=cnn_temperature,
)

mlp_test_prob = stable_softmax(
    mlp_test_logits,
    temperature=mlp_temperature,
)

ensemble_test_prob = (
    best_cnn_weight
    * cnn_test_prob
    + best_mlp_weight
    * mlp_test_prob
)

validate_probabilities(
    cnn_test_prob,
    expected_rows=len(x_test),
    name="CNN test probabilities",
)

validate_probabilities(
    mlp_test_prob,
    expected_rows=len(x_test),
    name="MLP test probabilities",
)

validate_probabilities(
    ensemble_test_prob,
    expected_rows=len(x_test),
    name="Initial ensemble test probabilities",
)

TEST_INFERENCE_SECONDS_BEFORE_TTA = float(
    time.perf_counter()
    - test_prediction_started
)

sorted_test_prob = np.sort(
    ensemble_test_prob,
    axis=1,
)

test_confidence = sorted_test_prob[
    :,
    -1,
]

test_margin = (
    sorted_test_prob[
        :,
        -1,
    ]
    - sorted_test_prob[
        :,
        -2,
    ]
)

uncertain_mask = (
    (
        test_confidence
        < TEST_CONFIDENCE
    )
    | (
        test_margin
        < TEST_MARGIN
    )
)

print(
    "Uncertain test images:",
    int(
        uncertain_mask.sum()
    ),
    "/",
    len(x_test),
)

print(
    "Initial inference seconds:",
    f"{TEST_INFERENCE_SECONDS_BEFORE_TTA:,.2f}",
)

# Cell 25 — Confidence-triggered test-time augmentation

def zero_padded_shift(
    images: np.ndarray,
    vertical_shift: int,
    horizontal_shift: int,
) -> np.ndarray:
    shifted = np.roll(
        images,
        shift=(
            vertical_shift,
            horizontal_shift,
        ),
        axis=(
            1,
            2,
        ),
    ).copy()

    if vertical_shift > 0:
        shifted[
            :,
            :vertical_shift,
            :,
            :,
        ] = 0

    elif vertical_shift < 0:
        shifted[
            :,
            vertical_shift:,
            :,
            :,
        ] = 0

    if horizontal_shift > 0:
        shifted[
            :,
            :,
            :horizontal_shift,
            :,
        ] = 0

    elif horizontal_shift < 0:
        shifted[
            :,
            :,
            horizontal_shift:,
            :,
        ] = 0

    return shifted


tta_started = time.perf_counter()
accepted_tta_count = 0

if uncertain_mask.any():
    uncertain_images = (
        x_test[
            uncertain_mask
        ]
    )

    tta_cnn_prob = np.zeros(
        (
            len(uncertain_images),
            10,
        ),
        dtype=np.float32,
    )

    for (
        vertical_shift,
        horizontal_shift,
    ) in TTA_SHIFTS:
        shifted_images = (
            zero_padded_shift(
                images=uncertain_images,
                vertical_shift=vertical_shift,
                horizontal_shift=(
                    horizontal_shift
                ),
            )
        )

        shifted_logits = (
            predict_logits(
                model=cnn,
                features=shifted_images,
            )
        )

        tta_cnn_prob += (
            stable_softmax(
                shifted_logits,
                temperature=(
                    cnn_temperature
                ),
            )
        )

    tta_cnn_prob /= float(
        len(TTA_SHIFTS)
    )

    validate_probabilities(
        tta_cnn_prob,
        expected_rows=len(
            uncertain_images
        ),
        name="TTA CNN probabilities",
    )

    recovered_probabilities = (
        best_cnn_weight
        * tta_cnn_prob
        + best_mlp_weight
        * mlp_test_prob[
            uncertain_mask
        ]
    )

    validate_probabilities(
        recovered_probabilities,
        expected_rows=len(
            uncertain_images
        ),
        name="Recovered ensemble probabilities",
    )

    original_probabilities = (
        ensemble_test_prob[
            uncertain_mask
        ]
    )

    original_sorted = np.sort(
        original_probabilities,
        axis=1,
    )

    recovered_sorted = np.sort(
        recovered_probabilities,
        axis=1,
    )

    original_quality = (
        original_sorted[
            :,
            -1,
        ]
        + (
            original_sorted[
                :,
                -1,
            ]
            - original_sorted[
                :,
                -2,
            ]
        )
    )

    recovered_quality = (
        recovered_sorted[
            :,
            -1,
        ]
        + (
            recovered_sorted[
                :,
                -1,
            ]
            - recovered_sorted[
                :,
                -2,
            ]
        )
    )

    accept_recovery = (
        recovered_quality
        >= original_quality
    )

    uncertain_indices = (
        np.flatnonzero(
            uncertain_mask
        )
    )

    accepted_indices = (
        uncertain_indices[
            accept_recovery
        ]
    )

    ensemble_test_prob[
        accepted_indices
    ] = recovered_probabilities[
        accept_recovery
    ]

    accepted_tta_count = int(
        len(accepted_indices)
    )

    print(
        "Accepted TTA replacements:",
        accepted_tta_count,
    )

else:
    print(
        "No test images required TTA."
    )

TTA_INFERENCE_SECONDS = float(
    time.perf_counter()
    - tta_started
)

validate_probabilities(
    ensemble_test_prob,
    expected_rows=len(x_test),
    name="Final ensemble test probabilities",
)

print(
    "TTA seconds:",
    f"{TTA_INFERENCE_SECONDS:,.2f}",
)

# Cell 26 — Create submission and detailed prediction outputs

test_labels = ensemble_test_prob.argmax(
    axis=1
).astype(
    np.int64
)

final_sorted_probabilities = np.sort(
    ensemble_test_prob,
    axis=1,
)

final_confidence = (
    final_sorted_probabilities[
        :,
        -1,
    ]
)

final_margin = (
    final_sorted_probabilities[
        :,
        -1,
    ]
    - final_sorted_probabilities[
        :,
        -2,
    ]
)

assert test_labels.shape == (
    len(x_test),
)

assert set(
    np.unique(
        test_labels
    ).tolist()
).issubset(
    set(range(10))
)

submission = pd.DataFrame(
    {
        "ImageId": np.arange(
            1,
            len(test_labels) + 1,
            dtype=np.int64,
        ),
        "Label": test_labels,
    }
)

prediction_details = pd.DataFrame(
    {
        "ImageId": submission[
            "ImageId"
        ],
        "PredictedLabel": test_labels,
        "Confidence": final_confidence,
        "TopTwoMargin": final_margin,
        "TTAEligible": uncertain_mask,
    }
)

for digit in range(10):
    prediction_details[
        f"ProbabilityDigit{digit}"
    ] = ensemble_test_prob[
        :,
        digit,
    ]

SUBMISSION_PATH = (
    OUTPUT_DIR
    / "submission.csv"
)

PREDICTION_DETAILS_PATH = (
    MODEL_EXPORT_DIR
    / "test_prediction_details.csv"
)

submission.to_csv(
    SUBMISSION_PATH,
    index=False,
)

prediction_details.to_csv(
    PREDICTION_DETAILS_PATH,
    index=False,
)

assert SUBMISSION_PATH.exists()
assert SUBMISSION_PATH.stat().st_size > 0
assert len(submission) == len(x_test)
assert submission.columns.tolist() == [
    "ImageId",
    "Label",
]

if SAMPLE_SUBMISSION_PATH is not None:
    sample_submission = pd.read_csv(
        SAMPLE_SUBMISSION_PATH
    )

    if RUN_MODE == "full":
        assert submission.shape == sample_submission.shape
        assert submission.columns.tolist() == (
            sample_submission.columns.tolist()
        )

display(submission.head(20))
display(
    prediction_details
    .sort_values(
        "Confidence"
    )
    .head(20)
)

print("Submission saved:", SUBMISSION_PATH)

# Cell 27 — Inspect the least-confident test predictions

inspection_count = min(
    20,
    len(x_test),
)

inspection_order = np.argsort(
    final_confidence
    + final_margin
)[:inspection_count]

rows = 4
columns = 5

fig, axes = plt.subplots(
    rows,
    columns,
    figsize=(10, 8),
)

for axis in axes.ravel():
    axis.axis("off")

for axis, index in zip(
    axes.ravel(),
    inspection_order,
):
    predicted_digit = int(
        test_labels[index]
    )

    axis.imshow(
        x_test[
            index,
            :,
            :,
            0,
        ],
        cmap="gray",
    )

    axis.set_title(
        f"ID {index + 1}: {predicted_digit}\n"
        f"p={final_confidence[index]:.3f}, "
        f"m={final_margin[index]:.3f}"
    )

    axis.axis("off")

plt.tight_layout()
plt.show()

# Cell 28 — Optional TensorFlow gradient-based global pixel importance

IMPORTANCE_CSV_PATH = (
    MODEL_EXPORT_DIR
    / "feature_importance.csv"
)

IMPORTANCE_IMAGE_PATH = (
    MODEL_EXPORT_DIR
    / "feature_importance.png"
)

def cnn_gradient_importance(
    model: keras.Model,
    images: np.ndarray,
    batch_size: int = 256,
) -> np.ndarray:
    importance = np.zeros(
        (
            28,
            28,
        ),
        dtype=np.float64,
    )

    for start in range(
        0,
        len(images),
        batch_size,
    ):
        image_batch = tf.convert_to_tensor(
            images[
                start:
                start + batch_size
            ],
            dtype=tf.float32,
        )

        with tf.GradientTape() as tape:
            tape.watch(
                image_batch
            )

            logits = model(
                image_batch,
                training=False,
            )

            predicted_classes = tf.argmax(
                logits,
                axis=1,
            )

            selected_logits = tf.gather(
                logits,
                predicted_classes,
                batch_dims=1,
            )

        gradients = tape.gradient(
            selected_logits,
            image_batch,
        )

        if gradients is None:
            raise RuntimeError(
                "CNN gradient calculation returned None."
            )

        importance += tf.reduce_sum(
            tf.abs(gradients),
            axis=(
                0,
                3,
            ),
        ).numpy()

    return (
        importance
        / max(
            len(images),
            1,
        )
    )


def mlp_backprojected_importance(
    model: keras.Model,
    reduced_features: np.ndarray,
    fitted_pca: PCA,
) -> np.ndarray:
    feature_tensor = tf.convert_to_tensor(
        reduced_features.astype(
            np.float32
        )
    )

    with tf.GradientTape() as tape:
        tape.watch(
            feature_tensor
        )

        logits = model(
            feature_tensor,
            training=False,
        )

        predicted_classes = tf.argmax(
            logits,
            axis=1,
        )

        selected_logits = tf.gather(
            logits,
            predicted_classes,
            batch_dims=1,
        )

    reduced_gradient = tape.gradient(
        selected_logits,
        feature_tensor,
    )

    if reduced_gradient is None:
        raise RuntimeError(
            "MLP gradient calculation returned None."
        )

    component_importance = tf.reduce_mean(
        tf.abs(
            reduced_gradient
        ),
        axis=0,
    ).numpy()

    pixel_importance = (
        np.abs(
            fitted_pca.components_
        ).T
        @ component_importance
    )

    return pixel_importance.reshape(
        28,
        28,
    )


if RUN_FEATURE_IMPORTANCE:
    importance_sample_size = min(
        FEATURE_IMPORTANCE_SAMPLE_SIZE,
        len(x_holdout),
    )

    cnn_importance = (
        cnn_gradient_importance(
            model=cnn,
            images=x_holdout[
                :importance_sample_size
            ],
        )
    )

    mlp_importance = (
        mlp_backprojected_importance(
            model=mlp,
            reduced_features=z_holdout[
                :importance_sample_size
            ],
            fitted_pca=pca,
        )
    )

    cnn_importance /= (
        cnn_importance.sum()
        + 1e-12
    )

    mlp_importance /= (
        mlp_importance.sum()
        + 1e-12
    )

    combined_importance = (
        best_cnn_weight
        * cnn_importance
        + best_mlp_weight
        * mlp_importance
    )

    assert np.isfinite(
        combined_importance
    ).all()

    assert combined_importance.shape == (
        28,
        28,
    )

    importance_df = pd.DataFrame(
        {
            "Pixel": np.arange(784),
            "Row": np.repeat(
                np.arange(28),
                28,
            ),
            "Column": np.tile(
                np.arange(28),
                28,
            ),
            "Importance": (
                combined_importance.ravel()
            ),
        }
    ).sort_values(
        "Importance",
        ascending=False,
    )

    importance_df.to_csv(
        IMPORTANCE_CSV_PATH,
        index=False,
    )

    fig, axis = plt.subplots(
        figsize=(6, 5)
    )

    image = axis.imshow(
        combined_importance,
        cmap="inferno",
    )

    axis.set_title(
        "Ensemble Global Pixel Importance"
    )

    axis.axis("off")

    fig.colorbar(
        image,
        ax=axis,
    )

    plt.tight_layout()

    plt.savefig(
        IMPORTANCE_IMAGE_PATH,
        dpi=180,
        bbox_inches="tight",
    )

    plt.show()

    display(
        importance_df.head(20)
    )

else:
    importance_df = pd.DataFrame()

    print(
        "Feature importance is disabled."
    )

# Cell 29 — Save the final Keras models and PCA transformer

FINAL_CNN_PATH = (
    MODEL_EXPORT_DIR
    / "residual_cnn.keras"
)

FINAL_MLP_PATH = (
    MODEL_EXPORT_DIR
    / "pca_mlp.keras"
)

PCA_PATH = (
    MODEL_EXPORT_DIR
    / "pca_transform.joblib"
)

cnn.save(
    FINAL_CNN_PATH
)

mlp.save(
    FINAL_MLP_PATH
)

joblib.dump(
    pca,
    PCA_PATH,
)

for path in [
    FINAL_CNN_PATH,
    FINAL_MLP_PATH,
    PCA_PATH,
]:
    assert path.exists(), (
        f"Missing saved artifact: {path}"
    )

    assert path.stat().st_size > 0, (
        f"Saved artifact is empty: {path}"
    )

print("Saved CNN:", FINAL_CNN_PATH)
print("Saved MLP:", FINAL_MLP_PATH)
print("Saved PCA:", PCA_PATH)

# Cell 30 — Save ensemble configuration and class labels

CLASS_LABELS_PATH = (
    MODEL_EXPORT_DIR
    / "class_labels.json"
)

ENSEMBLE_CONFIG_PATH = (
    MODEL_EXPORT_DIR
    / "ensemble_config.json"
)

class_labels = {
    "labels": list(range(10)),
    "label_names": [
        str(digit)
        for digit in range(10)
    ],
}

ensemble_config = {
    "owner": OWNER,
    "model_title": MODEL_TITLE,
    "model_handle": MODEL_HANDLE,
    "model_variation_slug": (
        MODEL_VARIATION_SLUG
    ),
    "primary_framework": (
        PRIMARY_FRAMEWORK
    ),
    "keras_backend": (
        keras.backend.backend()
    ),
    "rcnn_definition": (
        RCNN_DEFINITION
    ),
    "input_shape": [
        28,
        28,
        1,
    ],
    "flat_input_features": 784,
    "pixel_scale_divisor": 255.0,
    "class_labels": list(range(10)),
    "pca_components": int(
        pca.n_components_
    ),
    "pca_whiten": bool(
        pca.whiten
    ),
    "pca_explained_variance": (
        PCA_EXPLAINED_VARIANCE
    ),
    "cnn_weight": float(
        best_cnn_weight
    ),
    "mlp_weight": float(
        best_mlp_weight
    ),
    "cnn_temperature": float(
        cnn_temperature
    ),
    "mlp_temperature": float(
        mlp_temperature
    ),
    "test_confidence_threshold": (
        float(
            TEST_CONFIDENCE
        )
    ),
    "test_margin_threshold": float(
        TEST_MARGIN
    ),
    "tta_shifts": [
        [
            int(vertical),
            int(horizontal),
        ]
        for vertical, horizontal in TTA_SHIFTS
    ],
    "random_seed": int(SEED),
    "run_mode": RUN_MODE,
}

with CLASS_LABELS_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        class_labels,
        file,
        indent=2,
    )

with ENSEMBLE_CONFIG_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        ensemble_config,
        file,
        indent=2,
    )

assert CLASS_LABELS_PATH.exists()
assert ENSEMBLE_CONFIG_PATH.exists()

print("Saved class labels:", CLASS_LABELS_PATH)
print("Saved ensemble configuration:", ENSEMBLE_CONFIG_PATH)

# Cell 31 — Save metrics, implementation details, and runtime measurements

MODEL_METRICS_PATH = (
    MODEL_EXPORT_DIR
    / "model_metrics.json"
)

MODEL_STATS_PATH = (
    MODEL_EXPORT_DIR
    / "model_stats.json"
)

model_metrics = {
    "cnn_blend_accuracy": (
        cnn_blend_accuracy
    ),
    "mlp_blend_accuracy": (
        mlp_blend_accuracy
    ),
    "selected_blend_accuracy": (
        best_ensemble_accuracy
    ),
    "selected_blend_log_loss": (
        best_ensemble_loss
    ),
    "cnn_holdout_accuracy": (
        cnn_holdout_accuracy
    ),
    "mlp_holdout_accuracy": (
        mlp_holdout_accuracy
    ),
    "ensemble_holdout_accuracy": (
        ensemble_holdout_accuracy
    ),
    "cnn_holdout_log_loss": (
        cnn_holdout_log_loss
    ),
    "mlp_holdout_log_loss": (
        mlp_holdout_log_loss
    ),
    "ensemble_holdout_log_loss": (
        ensemble_holdout_log_loss
    ),
    "ensemble_holdout_ece_15_bins": (
        ensemble_holdout_ece
    ),
    "cnn_weight": float(
        best_cnn_weight
    ),
    "mlp_weight": float(
        best_mlp_weight
    ),
    "cnn_temperature": float(
        cnn_temperature
    ),
    "mlp_temperature": float(
        mlp_temperature
    ),
    "training_rows": int(
        len(x_train)
    ),
    "mining_rows": int(
        len(x_mine)
    ),
    "blend_rows": int(
        len(x_blend)
    ),
    "holdout_rows": int(
        len(x_holdout)
    ),
    "test_rows": int(
        len(x_test)
    ),
    "uncertain_test_images": int(
        uncertain_mask.sum()
    ),
    "accepted_tta_replacements": (
        accepted_tta_count
    ),
}

model_stats = {
    "cnn_parameter_count": (
        CNN_PARAMETER_COUNT
    ),
    "mlp_parameter_count": (
        MLP_PARAMETER_COUNT
    ),
    "combined_neural_parameter_count": int(
        CNN_PARAMETER_COUNT
        + MLP_PARAMETER_COUNT
    ),
    "pca_components": int(
        pca.n_components_
    ),
    "pca_explained_variance": (
        PCA_EXPLAINED_VARIANCE
    ),
    "cnn_training_seconds": (
        CNN_TRAINING_SECONDS
    ),
    "mlp_training_seconds": (
        MLP_TRAINING_SECONDS
    ),
    "pca_training_seconds": (
        PCA_TRAINING_SECONDS
    ),
    "test_inference_seconds_before_tta": (
        TEST_INFERENCE_SECONDS_BEFORE_TTA
    ),
    "tta_seconds": (
        TTA_INFERENCE_SECONDS
    ),
    "python_version": (
        platform.python_version()
    ),
    "keras_version": (
        keras.__version__
    ),
    "keras_backend": (
        keras.backend.backend()
    ),
    "tensorflow_version": (
        tf.__version__
    ),
    "scikit_learn_version": (
        sklearn.__version__
    ),
    "precision_policy": str(
        keras.mixed_precision.global_policy()
    ),
    "mixed_precision_enabled": USE_MIXED_PRECISION,
    "gpu_name": GPU_NAME,
    "gpu_compute_capability": GPU_COMPUTE_CAPABILITY,
    "layout_optimizer_enabled": False,
    "jit_compile_enabled": False,
    "gpu_devices": [
        device.name
        for device in (
            tf.config.list_physical_devices(
                "GPU"
            )
        )
    ],
    "deterministic_operations": (
        DETERMINISTIC_OPS
    ),
    "energy_consumption_measured": False,
}

with MODEL_METRICS_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        model_metrics,
        file,
        indent=2,
    )

with MODEL_STATS_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        model_stats,
        file,
        indent=2,
    )

display(
    pd.DataFrame(
        [
            {
                "Metric": key,
                "Value": value,
            }
            for key, value in (
                model_metrics.items()
            )
        ]
    )
)

# Cell 32 — Create the public model card

MODEL_CARD_PATH = (
    MODEL_EXPORT_DIR
    / "MODEL_CARD.md"
)

model_card_text = f"""
# MLP CNN RCNN Ensemble

**Kaggle model:** `patrickoneil/mlp-cnn-rcnn-ensemble`  
**Owner:** Patrick C O'Neil  
**Primary framework:** Keras  
**Backend:** TensorFlow  
**Task:** Ten-class handwritten-digit classification  
**RCNN definition:** Residual convolutional neural network  

## Model summary

This Keras-first ensemble combines a residual CNN operating on
28 × 28 grayscale images with a multilayer perceptron operating on
{int(pca.n_components_)} whitened PCA components. The two branches are
temperature-calibrated and combined using a blend-set-selected probability
weight. Low-confidence or low-margin test images may receive zero-padded
one-pixel translation test-time augmentation.

The model was trained from scratch. No pretrained weights or external
labeled data were used.

## Inputs and outputs

- CSV input: `pixel0` through `pixel783`, values from 0 through 255
- CNN tensor: `(N, 28, 28, 1)`, float32, normalized to `[0, 1]`
- MLP tensor: `(N, {int(pca.n_components_)})` PCA features
- Probability output: `(N, 10)`
- Label output: `(N,)`, digits 0 through 9

## Architecture

### Residual CNN

- Initial 32-filter convolution
- Residual stages with 32, 64, and 128 filters
- Downsampling at the first 64- and 128-filter blocks
- Final 192-filter convolution
- Global average pooling
- 192-unit dense layer
- Ten output logits

CNN parameters: {CNN_PARAMETER_COUNT:,}

### PCA-MLP

- Whitened PCA with {int(pca.n_components_)} components
- Dense 768
- Dense 384
- Dense 160
- Ten output logits

MLP parameters: {MLP_PARAMETER_COUNT:,}

Combined neural parameters: {CNN_PARAMETER_COUNT + MLP_PARAMETER_COUNT:,}

## Data split

- Training: {len(x_train):,} rows
- Hard-example mining: {len(x_mine):,} rows
- Blend/calibration: {len(x_blend):,} rows
- Untouched holdout: {len(x_holdout):,} rows

## Evaluation results

| Metric | Value |
|---|---:|
| CNN holdout accuracy | {cnn_holdout_accuracy:.6f} |
| MLP holdout accuracy | {mlp_holdout_accuracy:.6f} |
| Ensemble holdout accuracy | {ensemble_holdout_accuracy:.6f} |
| Ensemble holdout log loss | {ensemble_holdout_log_loss:.6f} |
| Ensemble holdout ECE | {ensemble_holdout_ece:.6f} |
| Blend accuracy | {best_ensemble_accuracy:.6f} |
| Blend log loss | {best_ensemble_loss:.6f} |
| CNN weight | {best_cnn_weight:.3f} |
| MLP weight | {best_mlp_weight:.3f} |
| CNN temperature | {cnn_temperature:.3f} |
| MLP temperature | {mlp_temperature:.3f} |

## Intended use

- Kaggle Digit Recognizer inference
- Educational digit-recognition experiments
- Keras ensemble and calibration demonstrations
- MNIST-style isolated grayscale digit classification

## Limitations

The model is not designed for photographs, letters, multi-digit documents,
identity verification, signature authentication, biometrics, or
safety-critical decisions. Performance may degrade under distribution shift,
incorrect polarity, severe rotation, cropping, blur, occlusion, unusual
stroke width, or mismatched preprocessing.

All artifacts from one model version must remain together:

- `residual_cnn.keras`
- `pca_mlp.keras`
- `pca_transform.joblib`
- `ensemble_config.json`
- `class_labels.json`

## Fairness and ethics

The source dataset does not provide demographic attributes. No demographic
fairness claim is made. Per-digit precision, recall, and F1 are provided in
`classification_report.csv`. Predictions should be reviewed before use in
consequential workflows.

## License

Recommended artifact license: Apache 2.0. This does not relicense Kaggle
competition data or third-party dependencies.
""".strip()

MODEL_CARD_PATH.write_text(
    model_card_text,
    encoding="utf-8",
)

assert MODEL_CARD_PATH.exists()
assert MODEL_CARD_PATH.stat().st_size > 0

print("Saved model card:", MODEL_CARD_PATH)

# Cell 33 — Create standalone public inference code

INFERENCE_SCRIPT_PATH = (
    MODEL_EXPORT_DIR
    / "inference.py"
)

inference_script = r"""
import os

os.environ.setdefault(
    "KERAS_BACKEND",
    "tensorflow",
)

import json
from pathlib import Path

import joblib
import keras
import numpy as np
import pandas as pd


class DigitEnsemble:
    def __init__(
        self,
        model_directory,
    ):
        self.model_directory = Path(
            model_directory
        )

        self.cnn = keras.models.load_model(
            self.model_directory
            / "residual_cnn.keras",
            compile=False,
        )

        self.mlp = keras.models.load_model(
            self.model_directory
            / "pca_mlp.keras",
            compile=False,
        )

        self.pca = joblib.load(
            self.model_directory
            / "pca_transform.joblib"
        )

        with (
            self.model_directory
            / "ensemble_config.json"
        ).open(
            "r",
            encoding="utf-8",
        ) as file:
            self.config = json.load(
                file
            )

        expected_labels = list(
            range(10)
        )

        if (
            self.config[
                "class_labels"
            ]
            != expected_labels
        ):
            raise ValueError(
                "Unexpected class-label order."
            )

    @staticmethod
    def _softmax(
        logits,
        temperature,
    ):
        logits = np.asarray(
            logits,
            dtype=np.float64,
        )

        temperature = float(
            temperature
        )

        if temperature <= 0:
            raise ValueError(
                "Temperature must be positive."
            )

        scaled = logits / temperature
        scaled -= scaled.max(
            axis=1,
            keepdims=True,
        )

        exponentials = np.exp(
            scaled
        )

        probability = exponentials / (
            exponentials.sum(
                axis=1,
                keepdims=True,
            )
        )

        return probability.astype(
            np.float32
        )

    @staticmethod
    def _validate_flat(
        flat,
        already_normalized,
    ):
        flat = np.asarray(
            flat,
            dtype=np.float32,
        )

        if flat.ndim == 1:
            flat = flat.reshape(
                1,
                -1,
            )

        if (
            flat.ndim != 2
            or flat.shape[1] != 784
        ):
            raise ValueError(
                "Input must have shape "
                "(N, 784)."
            )

        if not np.isfinite(
            flat
        ).all():
            raise ValueError(
                "Input contains NaN or "
                "infinite values."
            )

        if already_normalized:
            if (
                float(flat.min()) < 0.0
                or float(flat.max()) > 1.0
            ):
                raise ValueError(
                    "Normalized pixels must "
                    "be in [0, 1]."
                )
        else:
            if (
                float(flat.min()) < 0.0
                or float(flat.max()) > 255.0
            ):
                raise ValueError(
                    "Raw pixels must be "
                    "in [0, 255]."
                )

            flat = (
                flat
                / float(
                    255.0
                )
            )

        return flat

    def prepare(
        self,
        data,
        already_normalized=False,
    ):
        if isinstance(
            data,
            pd.DataFrame,
        ):
            pixel_columns = [
                f"pixel{index}"
                for index in range(784)
            ]

            missing = [
                column
                for column in pixel_columns
                if column
                not in data.columns
            ]

            if missing:
                raise ValueError(
                    "Missing required pixel "
                    f"columns: {missing[:5]}"
                )

            flat = data[
                pixel_columns
            ].to_numpy(
                dtype=np.float32
            )

        else:
            array = np.asarray(
                data
            )

            if (
                array.ndim == 4
                and array.shape[1:]
                == (
                    28,
                    28,
                    1,
                )
            ):
                flat = array.reshape(
                    -1,
                    784,
                )
            elif (
                array.ndim == 3
                and array.shape[1:]
                == (
                    28,
                    28,
                )
            ):
                flat = array.reshape(
                    -1,
                    784,
                )
            else:
                flat = array

        flat = self._validate_flat(
            flat,
            already_normalized=(
                already_normalized
            ),
        )

        images = flat.reshape(
            -1,
            28,
            28,
            1,
        )

        reduced = self.pca.transform(
            flat
        ).astype(
            np.float32
        )

        return (
            flat,
            images,
            reduced,
        )

    def predict_proba(
        self,
        data,
        already_normalized=False,
        batch_size=512,
    ):
        _, images, reduced = (
            self.prepare(
                data,
                already_normalized=(
                    already_normalized
                ),
            )
        )

        cnn_logits = self.cnn.predict(
            images,
            batch_size=batch_size,
            verbose=0,
        )

        mlp_logits = self.mlp.predict(
            reduced,
            batch_size=batch_size,
            verbose=0,
        )

        cnn_probability = self._softmax(
            cnn_logits,
            self.config[
                "cnn_temperature"
            ],
        )

        mlp_probability = self._softmax(
            mlp_logits,
            self.config[
                "mlp_temperature"
            ],
        )

        probability = (
            float(
                self.config[
                    "cnn_weight"
                ]
            )
            * cnn_probability
            + float(
                self.config[
                    "mlp_weight"
                ]
            )
            * mlp_probability
        )

        probability /= np.clip(
            probability.sum(
                axis=1,
                keepdims=True,
            ),
            1e-12,
            None,
        )

        if probability.shape != (
            len(images),
            10,
        ):
            raise RuntimeError(
                "Unexpected output shape."
            )

        if not np.isfinite(
            probability
        ).all():
            raise RuntimeError(
                "Probability output contains "
                "invalid values."
            )

        if not np.allclose(
            probability.sum(axis=1),
            1.0,
            atol=1e-5,
        ):
            raise RuntimeError(
                "Probability rows do not "
                "sum to one."
            )

        return probability

    def predict(
        self,
        data,
        already_normalized=False,
        batch_size=512,
    ):
        probability = self.predict_proba(
            data,
            already_normalized=(
                already_normalized
            ),
            batch_size=batch_size,
        )

        labels = probability.argmax(
            axis=1
        ).astype(
            np.int64
        )

        confidence = probability.max(
            axis=1
        )

        sorted_probability = np.sort(
            probability,
            axis=1,
        )

        margin = (
            sorted_probability[
                :,
                -1,
            ]
            - sorted_probability[
                :,
                -2,
            ]
        )

        return {
            "labels": labels,
            "probabilities": probability,
            "confidence": confidence,
            "top_two_margin": margin,
        }


if __name__ == "__main__":
    model = DigitEnsemble(
        Path(__file__).resolve().parent
    )

    print(
        "Loaded Keras digit ensemble "
        "successfully."
    )
""".strip()

INFERENCE_SCRIPT_PATH.write_text(
    inference_script,
    encoding="utf-8",
)

compile(
    inference_script,
    str(
        INFERENCE_SCRIPT_PATH
    ),
    "exec",
)

print(
    "Saved inference module:",
    INFERENCE_SCRIPT_PATH,
)

# Cell 34 — Create public usage documentation

USAGE_PATH = (
    MODEL_EXPORT_DIR
    / "USAGE.md"
)

usage_text = r"""
# Usage

The model is published as a coordinated Keras ensemble. Keep all files from
the same model version together.

```python
from pathlib import Path
import sys

import pandas as pd

MODEL_DIR = Path("${PATH}")

sys.path.insert(
    0,
    str(MODEL_DIR),
)

from inference import DigitEnsemble

model = DigitEnsemble(
    MODEL_DIR
)

test_frame = pd.read_csv(
    "/kaggle/input/digit-recognizer/test.csv"
)

result = model.predict(
    test_frame
)

print(result["labels"].shape)
print(result["probabilities"].shape)
print(result["confidence"][:5])
```

Inputs:

- DataFrame with `pixel0` through `pixel783`, values in `[0, 255]`
- Array with shape `(N, 784)`, `(N, 28, 28)`, or `(N, 28, 28, 1)`
- Set `already_normalized=True` only when array values are already in `[0, 1]`

Outputs:

- `labels`: shape `(N,)`
- `probabilities`: shape `(N, 10)`
- `confidence`: shape `(N,)`
- `top_two_margin`: shape `(N,)`

Known preventable failures:

- Dividing already-normalized values by 255 again
- Loading PCA and Keras files from different versions
- Passing RGB, inverted-polarity, multi-character, or non-28×28 inputs
- Changing digit-label ordering
- Omitting temperature calibration or ensemble weights
""".strip()

USAGE_PATH.write_text(
    usage_text,
    encoding="utf-8",
)

assert USAGE_PATH.exists()
print("Saved usage documentation:", USAGE_PATH)

# Cell 35 — Create Kaggle model metadata with Keras as primary framework

MODEL_METADATA_PATH = (
    MODEL_EXPORT_DIR
    / "model-metadata.json"
)

MODEL_INSTANCE_METADATA_PATH = (
    MODEL_EXPORT_DIR
    / "model-instance-metadata.json"
)

model_metadata = {
    "ownerSlug": "patrickoneil",
    "title": MODEL_TITLE,
    "slug": "mlp-cnn-rcnn-ensemble",
    "licenseName": "Apache 2.0",
    "subtitle": (
        "Calibrated Keras residual CNN and "
        "PCA-MLP ensemble for digit recognition"
    ),
    "isPrivate": False,
    "description": model_card_text,
    "publishTime": "",
    "provenanceSources": (
        "Kaggle Digit Recognizer competition "
        "training data; implementation by "
        "Patrick C O'Neil."
    ),
}

model_instance_metadata = {
    "ownerSlug": "patrickoneil",
    "modelSlug": "mlp-cnn-rcnn-ensemble",
    "instanceSlug": (
        MODEL_VARIATION_SLUG
    ),
    "framework": "keras",
    "overview": (
        "Keras-first two-branch digit classifier "
        "combining a residual CNN with a whitened "
        "PCA-MLP, temperature calibration, "
        "validation-selected blending, hard-example "
        "mining, and selective test-time augmentation."
    ),
    "usage": usage_text,
    "licenseName": "Apache 2.0",
    "fineTunable": True,
    "trainingData": [
        (
            "Kaggle Digit Recognizer "
            "competition train.csv"
        ),
        (
            "https://www.kaggle.com/"
            "competitions/digit-recognizer"
        ),
    ],
    "modelInstanceType": "Unspecified",
    "baseModelInstance": "",
    "externalBaseModelUrl": "",
}

with MODEL_METADATA_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        model_metadata,
        file,
        indent=2,
    )

with MODEL_INSTANCE_METADATA_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        model_instance_metadata,
        file,
        indent=2,
    )

assert (
    model_instance_metadata[
        "framework"
    ]
    == "keras"
)

print("Saved model metadata:", MODEL_METADATA_PATH)
print(
    "Saved Keras variation metadata:",
    MODEL_INSTANCE_METADATA_PATH,
)

# Cell 36 — Save requirements, citation, and upload instructions

REQUIREMENTS_PATH = (
    MODEL_EXPORT_DIR
    / "requirements.txt"
)

CITATION_PATH = (
    MODEL_EXPORT_DIR
    / "CITATION.bib"
)

UPLOAD_INSTRUCTIONS_PATH = (
    MODEL_EXPORT_DIR
    / "UPLOAD_INSTRUCTIONS.md"
)

requirements_text = f"""
keras=={keras.__version__}
tensorflow=={tf.__version__}
numpy
pandas
scikit-learn=={sklearn.__version__}
joblib
""".strip()

citation_text = r"""
@software{oneil_mlp_cnn_rcnn_ensemble_2026,
  author    = {Patrick C O'Neil},
  title     = {MLP CNN RCNN Ensemble},
  year      = {2026},
  publisher = {Kaggle Models},
  url       = {https://www.kaggle.com/models/patrickoneil/mlp-cnn-rcnn-ensemble}
}
""".strip()

upload_instructions_text = r"""
# Kaggle upload instructions

The parent model handle is:

`patrickoneil/mlp-cnn-rcnn-ensemble`

The Keras variation slug is:

`keras-digit-recognizer-ensemble`

The export folder contains `model-instance-metadata.json` and the complete
model artifacts.

Using the current Kaggle CLI:

```bash
kaggle models variations create \
  -p /path/to/mlp-cnn-rcnn-ensemble \
  -r skip
```

For a later version of an existing variation:

```bash
kaggle models variations versions create \
  patrickoneil/mlp-cnn-rcnn-ensemble/keras/keras-digit-recognizer-ensemble \
  -p /path/to/mlp-cnn-rcnn-ensemble \
  -n "Updated Keras ensemble artifacts" \
  -r skip
```

Review the installed Kaggle CLI help because command aliases can differ by
CLI version:

```bash
kaggle models variations --help
kaggle models instances --help
```
""".strip()

REQUIREMENTS_PATH.write_text(
    requirements_text,
    encoding="utf-8",
)

CITATION_PATH.write_text(
    citation_text,
    encoding="utf-8",
)

UPLOAD_INSTRUCTIONS_PATH.write_text(
    upload_instructions_text,
    encoding="utf-8",
)

print("Saved requirements:", REQUIREMENTS_PATH)
print("Saved citation:", CITATION_PATH)
print(
    "Saved upload instructions:",
    UPLOAD_INSTRUCTIONS_PATH,
)

# Cell 37 — Reload every saved artifact and verify inference equivalence

loaded_cnn = keras.models.load_model(
    FINAL_CNN_PATH,
    compile=False,
)

loaded_mlp = keras.models.load_model(
    FINAL_MLP_PATH,
    compile=False,
)

loaded_pca = joblib.load(
    PCA_PATH
)

with ENSEMBLE_CONFIG_PATH.open(
    "r",
    encoding="utf-8",
) as file:
    loaded_config = json.load(
        file
    )

verification_count = min(
    64,
    len(x_holdout),
)

verification_images = x_holdout[
    :verification_count
]

verification_flat = (
    verification_images.reshape(
        verification_count,
        784,
    )
)

verification_reduced = (
    loaded_pca.transform(
        verification_flat
    ).astype(
        np.float32
    )
)

original_cnn_logits = predict_logits(
    cnn,
    verification_images,
)

original_mlp_logits = predict_logits(
    mlp,
    verification_reduced,
)

loaded_cnn_logits = np.asarray(
    loaded_cnn.predict(
        verification_images,
        batch_size=verification_count,
        verbose=0,
    ),
    dtype=np.float32,
)

loaded_mlp_logits = np.asarray(
    loaded_mlp.predict(
        verification_reduced,
        batch_size=verification_count,
        verbose=0,
    ),
    dtype=np.float32,
)

original_probability = (
    best_cnn_weight
    * stable_softmax(
        original_cnn_logits,
        cnn_temperature,
    )
    + best_mlp_weight
    * stable_softmax(
        original_mlp_logits,
        mlp_temperature,
    )
)

loaded_probability = (
    float(
        loaded_config[
            "cnn_weight"
        ]
    )
    * stable_softmax(
        loaded_cnn_logits,
        loaded_config[
            "cnn_temperature"
        ],
    )
    + float(
        loaded_config[
            "mlp_weight"
        ]
    )
    * stable_softmax(
        loaded_mlp_logits,
        loaded_config[
            "mlp_temperature"
        ],
    )
)

validate_probabilities(
    loaded_probability,
    expected_rows=verification_count,
    name="Reloaded ensemble probabilities",
)

maximum_reload_difference = float(
    np.max(
        np.abs(
            original_probability
            - loaded_probability
        )
    )
)

assert maximum_reload_difference <= 1e-5, (
    "Reloaded model predictions differ from "
    f"the in-memory predictions by {maximum_reload_difference}."
)

assert np.array_equal(
    original_probability.argmax(
        axis=1
    ),
    loaded_probability.argmax(
        axis=1
    ),
)

assert (
    loaded_pca.n_components_
    == pca.n_components_
)

print(
    "Maximum reload probability difference:",
    maximum_reload_difference,
)

print(
    "Reloaded artifacts reproduce predictions."
)

# Cell 38 — Import and test the generated public inference module

import importlib.util

inference_spec = (
    importlib.util.spec_from_file_location(
        "digit_ensemble_inference",
        INFERENCE_SCRIPT_PATH,
    )
)

if (
    inference_spec is None
    or inference_spec.loader is None
):
    raise ImportError(
        "Could not create an import specification "
        "for inference.py."
    )

inference_module = (
    importlib.util.module_from_spec(
        inference_spec
    )
)

inference_spec.loader.exec_module(
    inference_module
)

public_model = (
    inference_module.DigitEnsemble(
        MODEL_EXPORT_DIR
    )
)

public_result = public_model.predict(
    verification_images,
    already_normalized=True,
    batch_size=verification_count,
)

assert public_result[
    "labels"
].shape == (
    verification_count,
)

assert public_result[
    "probabilities"
].shape == (
    verification_count,
    10,
)

assert np.allclose(
    public_result[
        "probabilities"
    ],
    loaded_probability,
    atol=1e-5,
)

print(
    "Public inference module validation passed."
)

# Cell 39 — Generate SHA-256 checksums and artifact manifest

MANIFEST_PATH = (
    MODEL_EXPORT_DIR
    / "artifact_manifest.json"
)

def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(
                chunk_size
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


manifest_records = []

for path in sorted(
    MODEL_EXPORT_DIR.iterdir()
):
    if (
        path.is_file()
        and path.name
        != MANIFEST_PATH.name
    ):
        manifest_records.append(
            {
                "filename": path.name,
                "size_bytes": int(
                    path.stat().st_size
                ),
                "sha256": sha256_file(
                    path
                ),
            }
        )

manifest = {
    "owner": OWNER,
    "model_handle": MODEL_HANDLE,
    "framework": "keras",
    "backend": "tensorflow",
    "artifacts": manifest_records,
}

with MANIFEST_PATH.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        manifest,
        file,
        indent=2,
    )

assert len(manifest_records) >= 10
assert all(
    record["size_bytes"] > 0
    for record in manifest_records
)

display(
    pd.DataFrame(
        manifest_records
    )
)

# Cell 40 — Create the upload package and perform final operational assertions

MODEL_ZIP_PATH = (
    OUTPUT_DIR
    / "mlp-cnn-rcnn-ensemble-keras-public.zip"
)

if MODEL_ZIP_PATH.exists():
    MODEL_ZIP_PATH.unlink()

with zipfile.ZipFile(
    MODEL_ZIP_PATH,
    mode="w",
    compression=zipfile.ZIP_DEFLATED,
) as archive:
    for path in sorted(
        MODEL_EXPORT_DIR.iterdir()
    ):
        if path.is_file():
            archive.write(
                path,
                arcname=path.name,
            )

required_artifacts = [
    FINAL_CNN_PATH,
    FINAL_MLP_PATH,
    PCA_PATH,
    ENSEMBLE_CONFIG_PATH,
    CLASS_LABELS_PATH,
    MODEL_METRICS_PATH,
    MODEL_STATS_PATH,
    MODEL_CARD_PATH,
    USAGE_PATH,
    INFERENCE_SCRIPT_PATH,
    MODEL_INSTANCE_METADATA_PATH,
    REQUIREMENTS_PATH,
    MANIFEST_PATH,
    SUBMISSION_PATH,
    MODEL_ZIP_PATH,
]

missing_artifacts = [
    str(path)
    for path in required_artifacts
    if not path.exists()
]

empty_artifacts = [
    str(path)
    for path in required_artifacts
    if (
        path.exists()
        and path.stat().st_size == 0
    )
]

assert not missing_artifacts, (
    "Missing required artifacts:\n"
    + "\n".join(
        missing_artifacts
    )
)

assert not empty_artifacts, (
    "Empty required artifacts:\n"
    + "\n".join(
        empty_artifacts
    )
)

assert np.isfinite(
    ensemble_holdout_accuracy
)

assert 0.0 <= ensemble_holdout_accuracy <= 1.0
assert 0.0 <= best_cnn_weight <= 1.0
assert 0.0 <= best_mlp_weight <= 1.0
assert np.isclose(
    best_cnn_weight + best_mlp_weight,
    1.0,
)

assert len(submission) == len(x_test)
assert submission["ImageId"].is_unique
assert submission["Label"].between(
    0,
    9,
).all()

print("=" * 72)
print("OPERATIONAL VALIDATION PASSED")
print("=" * 72)
print("Primary framework: Keras")
print("Backend: TensorFlow")
print("Model handle:", MODEL_HANDLE)
print("Run mode:", RUN_MODE)
print("Holdout accuracy:", f"{ensemble_holdout_accuracy:.6f}")
print("Submission:", SUBMISSION_PATH)
print("Model folder:", MODEL_EXPORT_DIR)
print("Upload ZIP:", MODEL_ZIP_PATH)
print()
print(
    "All required artifacts exist, are non-empty, "
    "reload successfully, and reproduce the in-memory predictions."
)
