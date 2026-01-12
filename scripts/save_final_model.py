"""
Script pour enregistrer le modèle final retenu
À exécuter après la sélection du meilleur modèle dans le notebook feature_engineering.ipynb
"""

from pathlib import Path
import joblib
import time

def save_final_model(best_model, best_model_name, X_train, y_train, output_dir="output/models"):
    """
    Entraîne le modèle final sur tout le dataset et l'enregistre
    
    Parameters:
    -----------
    best_model : modèle scikit-learn
        Le modèle retenu après comparaison
    best_model_name : str
        Nom du modèle retenu
    X_train : pd.DataFrame ou np.array
        Données d'entraînement (features)
    y_train : pd.Series ou np.array
        Variable cible d'entraînement
    output_dir : str
        Répertoire de sortie pour enregistrer le modèle
    """
    print("=" * 60)
    print("ENTRAÎNEMENT FINAL DU MODÈLE RETENU")
    print("=" * 60)
    print(f"Modèle retenu : {best_model_name}")
    print(f"Données d'entraînement : {X_train.shape[0]} observations, {X_train.shape[1]} features")
    
    # Entraînement du modèle final sur tout le dataset
    t0 = time.time()
    best_model.fit(X_train, y_train)
    fit_time = time.time() - t0
    
    print(f"\n✅ Modèle entraîné avec succès")
    print(f"⏱️  Temps d'entraînement : {fit_time:.2f} secondes")
    
    # Création du répertoire de sortie
    OUT_MODEL = Path(output_dir)
    OUT_MODEL.mkdir(parents=True, exist_ok=True)
    
    # Enregistrement du modèle final
    model_path = OUT_MODEL / "model_final.joblib"
    joblib.dump(best_model, model_path)
    
    # Enregistrement des métadonnées du modèle
    model_metadata = {
        "model_name": best_model_name,
        "model_type": type(best_model).__name__,
        "training_samples": X_train.shape[0],
        "training_features": X_train.shape[1],
        "fit_time_seconds": fit_time,
        "best_params": getattr(best_model, "best_params_", None) if hasattr(best_model, "best_params_") else None
    }
    
    metadata_path = OUT_MODEL / "model_metadata.joblib"
    joblib.dump(model_metadata, metadata_path)
    
    print(f"\n✅ Modèle enregistré avec succès")
    print(f"   - Modèle : {model_path}")
    print(f"   - Métadonnées : {metadata_path}")
    print(f"\n📊 Métadonnées du modèle :")
    for key, value in model_metadata.items():
        print(f"   - {key}: {value}")
    
    return model_path, metadata_path
