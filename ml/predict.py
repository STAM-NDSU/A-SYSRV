import pandas as pd
import pickle
import sqlite3
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

        # remove any row with NaN
        X = X.dropna()

        # log X shape
        logger.info(f"X shape: {X.shape}")

        # Load the model from file
        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)

        # Make predictions
        predictions = loaded_model.predict(X)

        predictions_df = pd.DataFrame(predictions, columns=['GO_0051287', 'GO_0009331', 'GO_0003677', 'GO_0003723', 'GO_0005506',
       'GO_0005524', 'GO_0046167', 'GO_0008270', 'GO_0016887', 'GO_0019843',
       'GO_0008654', 'GO_0046872', 'GO_0050661', 'GO_0051539'])
        

        return predictions_df

    except Exception as e:
        # Handle any exceptions (like file not found or data errors)
        print(f"An error occurred: {e}")
        return None
