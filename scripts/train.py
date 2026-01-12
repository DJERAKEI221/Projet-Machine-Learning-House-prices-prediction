import mlflow

with mlflow.start_run():
    print("Training started...")
    mlflow.log_param("example_param", 123)
    mlflow.log_metric("example_metric", 0.42)
    print("Training finished!")
