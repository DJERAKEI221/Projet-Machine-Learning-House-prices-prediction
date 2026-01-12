import argparse
import mlflow

def main(alpha: float):
    print("Training started...")
    
    # Exemple: on log le paramètre
    mlflow.log_param("alpha", alpha)
    
    # Ici tu mettras ton modèle
    # Ex: result = model.train(alpha)
    
    # On log une métrique de test
    mlflow.log_metric("score", 0.85)  # valeur bidon
    
    print("Training finished!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.5)
    args = parser.parse_args()
    
    with mlflow.start_run():
        main(args.alpha)
