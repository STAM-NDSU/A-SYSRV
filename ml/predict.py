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

        # Store and drop the 'id' column
        if 'primaryAccession' in df.columns:
            ids = df['primaryAccession']
            df = df.drop('primaryAccession', axis=1)

        # Split the data into features and targets
        X = df[df.columns[~df.columns.str.startswith('GO_')]].copy()

        # remove any row with NaN
        # X = X.dropna()

        for column in X.columns:
            X[column].fillna(X[column].mode()[0], inplace=True)

        # log X shape
        logger.info(f"X shape: {X.shape}")

        # Load the model from file
        with open(model_path, 'rb') as file:
            loaded_model = pickle.load(file)

        # Make predictions
        predictions = loaded_model.predict(X)

        # log length of predictions
        logger.info(f"Length of predictions: {len(predictions)}")

        predictions_df = pd.DataFrame(predictions, columns=['GO_0051287', 'GO_0009331', 'GO_0003677', 'GO_0003723', 'GO_0005506','GO_0005524', 'GO_0046167', 'GO_0008270', 'GO_0016887', 'GO_0019843','GO_0008654', 'GO_0046872', 'GO_0050661', 'GO_0051539'])
        
        # Add the 'id' column back
        predictions_df.insert(0, 'id', ids.values)

        # log predictions_df shape
        logger.info(f"predictions_df shape: {predictions_df.shape}")

        # Create a dictionary of IDs and their predicted GO terms
        predictions_dict = {}
        
        for _, row in predictions_df.iterrows():
            if len(predictions_dict) < 10:
                row_id = row['id']
                predicted_terms = [term for term, value in row.drop('id').items() if value == 1]
                if predicted_terms:
                    predictions_dict[row_id] = predicted_terms
            else:
                break

        # log length of predictions_dict    
        logger.info(f"Length of predictions_dict: {len(predictions_dict)}")
        

        return predictions_df, predictions_dict

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None
