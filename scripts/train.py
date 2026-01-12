import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_squared_error

with mlflow.start_run():
    mlflow.log_param("alpha", args.alpha)
    model = ...
    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)
    mlflow.log_metric("rmse", rmse)
    mlflow.sklearn.log_model(model, artifact_path="model")
