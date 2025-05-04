def tabpfn_predict(
    train_csv: str = "/mount/input/breast_cancer_train.csv",
    test_csv: str = "/mount/input/breast_cancer_test.csv",
    feature_columns: list = [
        "mean radius",
        "mean texture",
        "mean perimeter",
        "mean area",
        "mean smoothness",
        "mean compactness",
        "mean concavity",
        "mean concave points",
        "mean symmetry",
        "mean fractal dimension",
        "radius error",
        "texture error",
        "perimeter error",
        "area error",
        "smoothness error",
        "compactness error",
        "concavity error",
        "concave points error",
        "symmetry error",
        "fractal dimension error",
        "worst radius",
        "worst texture",
        "worst perimeter",
        "worst area",
        "worst smoothness",
        "worst compactness",
        "worst concavity",
        "worst concave points",
        "worst symmetry",
        "worst fractal dimension",
    ],
    target_column: str = "target",
) -> dict:
    """
    Train a predictor using TabPFN on a tabular dataset. Evaluate the predictor on the test set.

    Args:
        train_csv: Path to the CSV file containing the training data
        test_csv: Path to the CSV file containing the test data
        feature_columns: The names of the columns to use as features
        target_column: The name of the column to predict

    Returns:
        dict with the following structure:
        {
          'roc_auc': float  # The ROC AUC score of the predictor on the test set
          'accuracy': float  # The accuracy of the predictor on the test set
          'probs': list  # The probabilities of the predictor on the test set, as a list of floats (one per sample in the test set)
        }
    """
    # Adapted from https://github.com/PriorLabs/TabPFN?tab=readme-ov-file#classification

    import sys

    sys.path.append("/workspace/TabPFN")

    import pandas as pd
    from sklearn.metrics import accuracy_score, roc_auc_score
    from tabpfn import TabPFNClassifier

    # Load data
    train_df = pd.read_csv(train_csv)
    test_df = pd.read_csv(test_csv)
    X_train = train_df[feature_columns]
    y_train = train_df[target_column]
    X_test = test_df[feature_columns]
    y_test = test_df[target_column]

    # Initialize a classifier
    clf = TabPFNClassifier()
    clf.fit(X_train, y_train)

    # Predict probabilities
    prediction_probabilities = clf.predict_proba(X_test)
    roc_auc = roc_auc_score(y_test, prediction_probabilities[:, 1])
    print("ROC AUC:", roc_auc)

    # Predict labels
    predictions = clf.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print("Accuracy:", accuracy)

    return {
        "roc_auc": roc_auc,
        "accuracy": accuracy,
        "probs": prediction_probabilities[:, 1].tolist(),
    }
