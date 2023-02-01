# import libraries
import sys
from dvc import api
import pandas as pd
from io import StringIO
import logging
import logging.config
import warnings

from mlops_project.utils.logger import get_logging_config
import mlops_project.utils.paths as path

# Setting up logging configuration
logging.config.dictConfig(get_logging_config())

# Ignoring warnings
warnings.filterwarnings("ignore")

# Logging info message
logging.info('Fetching data...')

# Reading data from remote source
try:
    movie_data_path = api.read(path.data_raw_dir('movies.csv'), remote='data-track')
    finantial_data_path = api.read(path.data_raw_dir('finantials.csv'), remote='data-track')
    opening_data_path = api.read(path.data_raw_dir('opening_gross.csv'), remote='data-track')

    logging.info('Data fetched successfully.')

    # Reading data into pandas dataframes
    fin_data = pd.read_csv(StringIO(finantial_data_path))
    movie_data = pd.read_csv(StringIO(movie_data_path))
    opening_data = pd.read_csv(StringIO(opening_data_path))

except Exception as e:
    logging.error(f"Error fetching data: {str(e)}")
try:
    # Selecting only numeric columns and movie title column
    logging.info('Selecting only numeric columns and movie title column from movie data...')
    numeric_columns_mask = (movie_data.dtypes == float) | (movie_data.dtypes == int)
    numeric_columns = [column for column in numeric_columns_mask.index if numeric_columns_mask[column]]
    movie_data = movie_data[numeric_columns+['movie_title']]
    logging.info('Selection of numeric columns and movie title column from movie data completed.')

    # Selecting only movie title, production budget, and worldwide gross columns
    logging.info('Selecting only movie title, production budget, and worldwide gross columns from financial data...')
    fin_data = fin_data[['movie_title', 'production_budget', 'worldwide_gross']]
    logging.info('Selection of movie title, production budget, and worldwide gross columns from financial data completed.')

    # Merging financial and movie data
    logging.info('Merging financial and movie data...')
    fin_movie_data = pd.merge(fin_data, movie_data, on='movie_title', how='left')
    full_movie_data = pd.merge(opening_data, fin_movie_data, on='movie_title', how='left')
    logging.info('Merging of financial and movie data completed.')

    # Dropping unnecessary columns
    logging.info('Dropping unnecessary columns from the merged data...')
    full_movie_data = full_movie_data.drop(['gross','movie_title'], axis=1)
    logging.info('Data Cleaning Completed...')

    # Writing the processed data to a file
    logging.info('Saving Cleaned Data...')
    full_movie_data.to_csv(path.data_processed_dir('full_data.csv'),index=False)
    logging.info('Data Saved...')
    
    logging.info('Data Fetched and prepared...')
except Exception as e:
    logging.error(f"Error in data prepared.: {str(e)}")
