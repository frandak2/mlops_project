from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np
import pandas as pd

import logging
import logging.config
import warnings

import mlops_project.utils.paths as path
from mlops_project.utils.logger import get_logging_config
from mlops_project.utils.model_utils import update_model, save_simple_metrics_report, get_model_performance_test_set

# Setting up logging configuration
logging.config.dictConfig(get_logging_config())

# Ignoring warnings
warnings.filterwarnings("ignore")

logging.info('Loading Data...')
data = pd.read_csv(path.data_processed_dir('full_data.csv'))

logging.info('Loading model...')
model = Pipeline([
    ('imputer', SimpleImputer(strategy='mean',missing_values=np.nan)),
    ('core_model', GradientBoostingRegressor())
])

logging.info('Seraparating dataset into train and test')
X = data.drop(['worldwide_gross'], axis= 1)
y = data['worldwide_gross']

# Train and validate data
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.35, random_state=42)

# Train and test data
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.35, random_state=42)

logging.info('Setting Hyperparameter to tune')
param_tuning = {'core_model__n_estimators':range(20,301,20)}

grid_search = GridSearchCV(model, param_grid= param_tuning, scoring='r2', cv=5)


logging.info('Starting grid search...')
grid_search.fit(X_train, y_train)

logging.info('Cross validating with best model...')
final_result = cross_validate(grid_search.best_estimator_, X_train, y_train, return_train_score=True, cv=5)

train_score = np.mean(final_result['train_score'])
test_score = np.mean(final_result['test_score'])
assert train_score > 0.7
assert test_score > 0.65

logging.info(f'Train Score: {train_score}')
logging.info(f'Test Score: {test_score}')

logging.info('Updating model...')
update_model(grid_search.best_estimator_)

logging.info('Generating model report...')
validation_score = grid_search.best_estimator_.score(X_val, y_val)
save_simple_metrics_report(train_score, test_score, validation_score, grid_search.best_estimator_)

y_val_pred = grid_search.best_estimator_.predict(X_val)
get_model_performance_test_set(y_val, y_val_pred)

logging.info('Training Finished')