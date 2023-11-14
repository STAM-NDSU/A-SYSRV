import pandas as pd
import pickle
import sqlite3


def predict_with_model(db_path, model_path):
    """
    Loads data from a SQLite database and a model from a pickle file, then makes predictions using this model.

    Parameters:
    db_path (str): Path to the SQLite database file.
    model_path (str): Path to the saved model file (.pkl).

    Returns:
    Any: The predictions made by the model.
    """
    try:
        # Connect to the SQLite database and load data
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM new_merged_data", conn)

        # Split the data into features and targets
        X = df[df.columns[~df.columns.str.startswith('GO_')]]

        # Load the model from file
        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)

        # Make predictions
        predictions = loaded_model.predict(X)

        return predictions

    except Exception as e:
        # Handle any exceptions (like file not found or data errors)
        print(f"An error occurred: {e}")
        return None
