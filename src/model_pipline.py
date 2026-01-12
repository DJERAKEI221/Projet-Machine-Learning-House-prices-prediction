"""
Module pipeline modèle : load_data() + build_model()
Adapté à sklearn pour l'exemple.
"""

from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


def load_data():
    """ Retourne X_train, X_test, y_train, y_test """
    dataset = load_diabetes()
    X = dataset.data
    y = dataset.target

    return train_test_split(X, y, test_size=0.2, random_state=42)


def build_model():
    """ Retourne model, params """
    params = {
        "n_estimators": 150,
        "max_depth": 6
    }
    model = RandomForestRegressor(**params, random_state=42)
    return model, params
