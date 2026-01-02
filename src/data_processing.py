"""
Data processing module for house price prediction.
Handles data loading, cleaning, and preprocessing.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Class for processing and cleaning house price data."""
    
    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize DataProcessor.
        
        Args:
            data_dir: Path to directory containing raw data files
        """
        self.data_dir = Path(data_dir)
        self.train_df = None
        self.test_df = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load training and test datasets.
        
        Returns:
            Tuple of (train_df, test_df)
        """
        logger.info("Loading data from CSV files...")
        
        train_path = self.data_dir / "train.csv"
        test_path = self.data_dir / "test.csv"
        
        if not train_path.exists():
            raise FileNotFoundError(f"Training data not found at {train_path}")
        if not test_path.exists():
            raise FileNotFoundError(f"Test data not found at {test_path}")
            
        self.train_df = pd.read_csv(train_path)
        self.test_df = pd.read_csv(test_path)
        
        logger.info(f"Training data shape: {self.train_df.shape}")
        logger.info(f"Test data shape: {self.test_df.shape}")
        
        return self.train_df, self.test_df
    
    def handle_missing_values(self, df: pd.DataFrame, is_train: bool = True) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: DataFrame to process
            is_train: Whether this is training data (affects handling strategy)
            
        Returns:
            DataFrame with handled missing values
        """
        df = df.copy()
        
        # Identify missing values
        missing = df.isnull().sum()
        missing_pct = (missing / len(df)) * 100
        missing_df = pd.DataFrame({
            'Missing Count': missing,
            'Percentage': missing_pct
        }).sort_values('Missing Count', ascending=False)
        
        logger.info(f"Missing values summary:\n{missing_df[missing_df['Missing Count'] > 0]}")
        
        # Handle missing values based on data description
        # PoolQC: NA means no pool
        df['PoolQC'] = df['PoolQC'].fillna('None')
        
        # MiscFeature: NA means no miscellaneous feature
        df['MiscFeature'] = df['MiscFeature'].fillna('None')
        
        # Alley: NA means no alley access
        df['Alley'] = df['Alley'].fillna('None')
        
        # Fence: NA means no fence
        df['Fence'] = df['Fence'].fillna('None')
        
        # FireplaceQu: NA means no fireplace
        df['FireplaceQu'] = df['FireplaceQu'].fillna('None')
        
        # Garage features: NA means no garage
        garage_cols = ['GarageType', 'GarageFinish', 'GarageQual', 'GarageCond']
        for col in garage_cols:
            df[col] = df[col].fillna('None')
        
        df['GarageYrBlt'] = df['GarageYrBlt'].fillna(0)
        
        # Basement features: NA means no basement
        bsmt_cols = ['BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2']
        for col in bsmt_cols:
            df[col] = df[col].fillna('None')
        
        # Fill numeric basement columns with 0
        bsmt_numeric = ['BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF', 'TotalBsmtSF', 
                       'BsmtFullBath', 'BsmtHalfBath']
        for col in bsmt_numeric:
            df[col] = df[col].fillna(0)
        
        # MasVnrType and MasVnrArea
        df['MasVnrType'] = df['MasVnrType'].fillna('None')
        df['MasVnrArea'] = df['MasVnrArea'].fillna(0)
        
        # MSZoning: Use mode
        df['MSZoning'] = df['MSZoning'].fillna(df['MSZoning'].mode()[0])
        
        # Utilities: Use mode (most likely AllPub)
        df['Utilities'] = df['Utilities'].fillna(df['Utilities'].mode()[0])
        
        # Functional: Use mode
        df['Functional'] = df['Functional'].fillna(df['Functional'].mode()[0])
        
        # Electrical: Use mode
        df['Electrical'] = df['Electrical'].fillna(df['Electrical'].mode()[0])
        
        # KitchenQual: Use mode
        df['KitchenQual'] = df['KitchenQual'].fillna(df['KitchenQual'].mode()[0])
        
        # Exterior1st and Exterior2nd: Use mode
        df['Exterior1st'] = df['Exterior1st'].fillna(df['Exterior1st'].mode()[0])
        df['Exterior2nd'] = df['Exterior2nd'].fillna(df['Exterior2nd'].mode()[0])
        
        # SaleType: Use mode
        df['SaleType'] = df['SaleType'].fillna(df['SaleType'].mode()[0])
        
        # LotFrontage: Fill with median by neighborhood
        df['LotFrontage'] = df.groupby('Neighborhood')['LotFrontage'].transform(
            lambda x: x.fillna(x.median())
        )
        df['LotFrontage'] = df['LotFrontage'].fillna(df['LotFrontage'].median())
        
        # GarageCars and GarageArea: Fill with 0 (no garage)
        df['GarageCars'] = df['GarageCars'].fillna(0)
        df['GarageArea'] = df['GarageArea'].fillna(0)
        
        logger.info("Missing values handled successfully")
        
        return df
    
    def remove_outliers(self, df: pd.DataFrame, target_col: str = 'SalePrice') -> pd.DataFrame:
        """
        Remove outliers from the dataset based on target variable.
        
        Args:
            df: DataFrame to process
            target_col: Name of target column
            
        Returns:
            DataFrame with outliers removed
        """
        if target_col not in df.columns:
            return df
            
        df = df.copy()
        original_len = len(df)
        
        # Identifier les outliers avant suppression
        outlier_indices = []
        outlier_info = []
        
        # Outliers basés sur GrLivArea et SalePrice
        if 'GrLivArea' in df.columns:
            grliv_outliers = df[(df['GrLivArea'] > 4000) & (df[target_col] < 300000)]
            if len(grliv_outliers) > 0:
                outlier_indices.extend(grliv_outliers.index.tolist())
                outlier_info.append({
                    'type': 'GrLivArea > 4000 et SalePrice < 300000',
                    'count': len(grliv_outliers),
                    'indices': grliv_outliers.index.tolist()
                })
        
        # Outliers basés sur TotalBsmtSF
        if 'TotalBsmtSF' in df.columns:
            bsmt_outliers = df[df['TotalBsmtSF'] >= 3000]
            if len(bsmt_outliers) > 0:
                # Éviter les doublons
                new_indices = [idx for idx in bsmt_outliers.index.tolist() if idx not in outlier_indices]
                if new_indices:
                    outlier_indices.extend(new_indices)
                    outlier_info.append({
                        'type': 'TotalBsmtSF >= 3000',
                        'count': len(new_indices),
                        'indices': new_indices
                    })
        
        # Afficher les statistiques des outliers
        if outlier_indices:
            outliers_df = df.loc[outlier_indices]
            total_removed = len(outlier_indices)
            
            logger.info("=" * 80)
            logger.info(f"OUTLIERS DETECTES ET SUPPRIMES: {total_removed} observations")
            logger.info("=" * 80)
            
            # Détails par type d'outlier
            for info in outlier_info:
                logger.info(f"\nType: {info['type']}")
                logger.info(f"Nombre: {info['count']}")
            
            # Statistiques communes des outliers
            logger.info("\n" + "=" * 80)
            logger.info("CARACTERISTIQUES COMMUNES DES OUTLIERS:")
            logger.info("=" * 80)
            
            # Colonnes numériques importantes à analyser
            numeric_cols = ['GrLivArea', 'TotalBsmtSF', 'LotArea', 'YearBuilt', 
                          'OverallQual', 'OverallCond', 'GarageArea', target_col]
            numeric_cols = [col for col in numeric_cols if col in outliers_df.columns]
            
            if numeric_cols:
                logger.info("\nStatistiques descriptives (moyennes):")
                stats = outliers_df[numeric_cols].mean()
                for col, val in stats.items():
                    logger.info(f"  {col}: {val:.2f}")
                
                logger.info("\nComparaison avec le dataset complet:")
                for col in numeric_cols:
                    outlier_mean = outliers_df[col].mean()
                    dataset_mean = df[col].mean()
                    diff_pct = ((outlier_mean - dataset_mean) / dataset_mean) * 100
                    logger.info(f"  {col}:")
                    logger.info(f"    Outliers: {outlier_mean:.2f}")
                    logger.info(f"    Dataset: {dataset_mean:.2f}")
                    logger.info(f"    Difference: {diff_pct:+.2f}%")
            
            # Colonnes catégorielles importantes
            categorical_cols = ['Neighborhood', 'HouseStyle', 'MSZoning', 'SaleCondition', 
                              'BldgType', 'RoofStyle', 'ExterQual', 'KitchenQual']
            categorical_cols = [col for col in categorical_cols if col in outliers_df.columns]
            
            if categorical_cols:
                logger.info("\nValeurs les plus fréquentes dans les outliers:")
                for col in categorical_cols:
                    value_counts = outliers_df[col].value_counts()
                    if len(value_counts) > 0:
                        logger.info(f"  {col}:")
                        for val, count in value_counts.head(5).items():
                            pct = (count / len(outliers_df)) * 100
                            # Comparer avec le dataset complet
                            dataset_pct = (df[col].value_counts().get(val, 0) / len(df)) * 100
                            logger.info(f"    {val}: {count} ({pct:.1f}% des outliers, {dataset_pct:.1f}% du dataset)")
            
            # Analyse de similarité entre outliers
            logger.info("\n" + "=" * 80)
            logger.info("ANALYSE DE SIMILARITE ENTRE OUTLIERS:")
            logger.info("=" * 80)
            
            if len(outliers_df) > 1:
                # Identifier les caractéristiques communes (présentes dans au moins 50% des outliers)
                logger.info("\nCaracteristiques presentes dans au moins 50% des outliers:")
                
                # Pour les variables catégorielles
                for col in categorical_cols:
                    value_counts = outliers_df[col].value_counts()
                    common_values = value_counts[value_counts >= len(outliers_df) * 0.5]
                    if len(common_values) > 0:
                        logger.info(f"  {col}:")
                        for val, count in common_values.items():
                            pct = (count / len(outliers_df)) * 100
                            logger.info(f"    '{val}' present dans {count}/{len(outliers_df)} outliers ({pct:.1f}%)")
                
                # Pour les variables numériques - identifier les plages communes
                logger.info("\nPlages de valeurs communes pour les variables numeriques:")
                for col in numeric_cols:
                    if col != target_col:  # Exclure la variable cible
                        q25 = outliers_df[col].quantile(0.25)
                        q75 = outliers_df[col].quantile(0.75)
                        median_val = outliers_df[col].median()
                        min_val = outliers_df[col].min()
                        max_val = outliers_df[col].max()
                        
                        # Vérifier si les valeurs sont concentrées
                        iqr = q75 - q25
                        if iqr > 0:
                            cv = (iqr / median_val) * 100 if median_val > 0 else 0
                            logger.info(f"  {col}:")
                            logger.info(f"    Min: {min_val:.2f}, Max: {max_val:.2f}")
                            logger.info(f"    Median: {median_val:.2f}, IQR: {iqr:.2f}")
                            logger.info(f"    Coefficient de variation: {cv:.1f}%")
                            if cv < 30:
                                logger.info(f"    -> Valeurs relativement concentrees (similarite elevee)")
                            elif cv > 70:
                                logger.info(f"    -> Valeurs tres dispersees (peu de similarite)")
                
                # Identifier les outliers identiques ou très similaires
                logger.info("\n" + "-" * 80)
                logger.info("Outliers avec caracteristiques identiques ou tres similaires:")
                logger.info("-" * 80)
                
                # Comparer chaque outlier avec les autres
                similar_pairs = []
                key_cols = ['Neighborhood', 'HouseStyle', 'MSZoning', 'OverallQual', 'YearBuilt']
                key_cols = [col for col in key_cols if col in outliers_df.columns]
                
                if len(key_cols) > 0 and len(outliers_df) > 1:
                    for i, idx1 in enumerate(outlier_indices):
                        for idx2 in outlier_indices[i+1:]:
                            row1 = outliers_df.loc[idx1]
                            row2 = outliers_df.loc[idx2]
                            
                            # Compter les caractéristiques identiques
                            matches = sum(1 for col in key_cols if row1[col] == row2[col])
                            match_pct = (matches / len(key_cols)) * 100
                            
                            if match_pct >= 60:  # Au moins 60% de similarité
                                similar_pairs.append({
                                    'idx1': idx1,
                                    'idx2': idx2,
                                    'matches': matches,
                                    'match_pct': match_pct,
                                    'common_features': {col: row1[col] for col in key_cols if row1[col] == row2[col]}
                                })
                    
                    if similar_pairs:
                        for pair in similar_pairs:
                            logger.info(f"\n  Outliers {pair['idx1']} et {pair['idx2']}:")
                            logger.info(f"    Similarite: {pair['matches']}/{len(key_cols)} caracteristiques ({pair['match_pct']:.1f}%)")
                            logger.info(f"    Caracteristiques communes:")
                            for col, val in pair['common_features'].items():
                                logger.info(f"      {col}: {val}")
                    else:
                        logger.info("  Aucune paire d'outliers tres similaire trouvee.")
                
                # Profil type des outliers
                logger.info("\n" + "=" * 80)
                logger.info("PROFIL TYPE DES OUTLIERS:")
                logger.info("=" * 80)
                
                # Créer un profil "moyen" des outliers
                logger.info("\nProfil moyen (mode pour categoriel, mediane pour numerique):")
                
                for col in categorical_cols:
                    mode_val = outliers_df[col].mode()
                    if len(mode_val) > 0:
                        mode_count = (outliers_df[col] == mode_val.iloc[0]).sum()
                        mode_pct = (mode_count / len(outliers_df)) * 100
                        logger.info(f"  {col}: {mode_val.iloc[0]} (present dans {mode_pct:.1f}% des outliers)")
                
                for col in numeric_cols:
                    if col != target_col:
                        median_val = outliers_df[col].median()
                        logger.info(f"  {col}: {median_val:.2f} (mediane)")
            
            logger.info("\n" + "=" * 80)
            logger.info(f"Total supprime: {total_removed} outliers ({total_removed/original_len*100:.2f}% du dataset)")
            logger.info("=" * 80 + "\n")
        
        # Supprimer les outliers
        if 'GrLivArea' in df.columns:
            df = df[~((df['GrLivArea'] > 4000) & (df[target_col] < 300000))]
        
        if 'TotalBsmtSF' in df.columns:
            df = df[df['TotalBsmtSF'] < 3000]
        
        return df
    
    def transform_outliers(self, df: pd.DataFrame, target_col: str = 'SalePrice', 
                          method: str = 'contextual') -> pd.DataFrame:
        """
        Transform outliers instead of removing them using contextual methods.
        
        Args:
            df: DataFrame to process
            target_col: Name of target column
            method: Transformation method ('contextual', 'capping', 'winsorize')
            
        Returns:
            DataFrame with outliers transformed
        """
        if target_col not in df.columns:
            return df
            
        df = df.copy()
        original_len = len(df)
        transformations_applied = []
        
        logger.info("=" * 80)
        logger.info("TRANSFORMATION DES OUTLIERS")
        logger.info("=" * 80)
        
        # 1. Transformation pour GrLivArea > 4000 et SalePrice < 300000
        if 'GrLivArea' in df.columns:
            grliv_outliers = df[(df['GrLivArea'] > 4000) & (df[target_col] < 300000)]
            if len(grliv_outliers) > 0:
                logger.info(f"\nType 1: GrLivArea > 4000 et SalePrice < 300000")
                logger.info(f"Nombre d'outliers detectes: {len(grliv_outliers)}")
                
                if method == 'contextual':
                    # Méthode contextuelle : ajuster le prix selon la corrélation avec GrLivArea
                    # Utiliser la transformation logarithmique pour le prix
                    for idx in grliv_outliers.index:
                        grliv_area = df.loc[idx, 'GrLivArea']
                        old_price = df.loc[idx, target_col]
                        
                        # Trouver des maisons similaires (même quartier, qualité similaire)
                        similar_houses = df[
                            (df['GrLivArea'] > grliv_area * 0.8) & 
                            (df['GrLivArea'] < grliv_area * 1.2) &
                            (df.index != idx)
                        ]
                        
                        if len(similar_houses) > 0 and 'OverallQual' in df.columns:
                            # Filtrer par qualité similaire
                            qual = df.loc[idx, 'OverallQual']
                            similar_houses = similar_houses[
                                (similar_houses['OverallQual'] >= qual - 1) &
                                (similar_houses['OverallQual'] <= qual + 1)
                            ]
                        
                        if len(similar_houses) > 0:
                            # Travailler dans l'espace logarithmique
                            # Calculer log(prix) et log(surface) pour maisons similaires
                            log_prices = np.log1p(similar_houses[target_col])
                            log_areas = np.log1p(similar_houses['GrLivArea'])
                            
                            # Calculer la pente de la relation log-linéaire
                            # log(prix) = a + b * log(surface)
                            # Utiliser la corrélation et les écarts-types pour estimer b
                            if len(log_prices) > 1 and log_areas.std() > 0:
                                # Calculer la pente de régression simple
                                covariance = ((log_prices - log_prices.mean()) * 
                                            (log_areas - log_areas.mean())).sum()
                                variance_areas = ((log_areas - log_areas.mean()) ** 2).sum()
                                slope = covariance / variance_areas if variance_areas > 0 else 1.0
                                
                                # Intercept
                                intercept = log_prices.mean() - slope * log_areas.mean()
                            else:
                                # Fallback : utiliser le ratio moyen
                                slope = (log_prices / log_areas).mean()
                                intercept = log_prices.mean() - slope * log_areas.mean()
                            
                            # Calculer le log(prix) attendu pour cette surface
                            log_area_current = np.log1p(grliv_area)
                            log_price_new = intercept + slope * log_area_current
                            
                            # Retransformer en prix normal
                            new_price = np.expm1(log_price_new)
                            
                            # S'assurer que le nouveau prix est raisonnable
                            # Le nouveau prix doit être supérieur à l'ancien (on corrige un prix trop bas)
                            if new_price <= old_price:
                                # Si le nouveau prix est plus bas ou égal, utiliser une augmentation modérée
                                # Basée sur le percentile 75 des maisons similaires
                                p75_price = similar_houses[target_col].quantile(0.75)
                                new_price = max(old_price * 1.15, p75_price * 0.9)
                            
                            # Limiter au percentile 99 pour éviter les valeurs trop extrêmes
                            p99_price = df[target_col].quantile(0.99)
                            new_price = min(new_price, p99_price)
                            
                            df.loc[idx, target_col] = new_price
                            transformations_applied.append({
                                'index': idx,
                                'type': 'GrLivArea-SalePrice',
                                'variable': target_col,
                                'old_value': old_price,
                                'new_value': new_price,
                                'method': 'contextual_log_adjustment'
                            })
                            logger.info(f"  Index {idx}: Prix ajuste (log) de ${old_price:,.0f} a ${new_price:,.0f}")
                        else:
                            # Si pas de maisons similaires, utiliser capping dans l'espace log
                            log_prices_all = np.log1p(df[target_col])
                            p99_log_price = log_prices_all.quantile(0.99)
                            old_log_price = np.log1p(old_price)
                            
                            # Ajuster dans l'espace log (augmenter de 20% en log)
                            new_log_price = min(old_log_price + np.log1p(0.2), p99_log_price)
                            new_price = np.expm1(new_log_price)
                            
                            df.loc[idx, target_col] = new_price
                            transformations_applied.append({
                                'index': idx,
                                'type': 'GrLivArea-SalePrice',
                                'variable': target_col,
                                'old_value': old_price,
                                'new_value': new_price,
                                'method': 'log_capping_fallback'
                            })
                            logger.info(f"  Index {idx}: Prix ajuste (log capping) de ${old_price:,.0f} a ${new_price:,.0f}")
                
                elif method == 'capping':
                    # Capping simple : limiter GrLivArea au percentile 99
                    p99_grliv = df['GrLivArea'].quantile(0.99)
                    for idx in grliv_outliers.index:
                        old_grliv = df.loc[idx, 'GrLivArea']
                        df.loc[idx, 'GrLivArea'] = p99_grliv
                        transformations_applied.append({
                            'index': idx,
                            'type': 'GrLivArea-SalePrice',
                            'variable': 'GrLivArea',
                            'old_value': old_grliv,
                            'new_value': p99_grliv,
                            'method': 'capping'
                        })
                        logger.info(f"  Index {idx}: GrLivArea ajuste de {old_grliv:.0f} a {p99_grliv:.0f}")
        
        # 2. Transformation pour TotalBsmtSF >= 3000
        if 'TotalBsmtSF' in df.columns:
            bsmt_outliers = df[df['TotalBsmtSF'] >= 3000]
            if len(bsmt_outliers) > 0:
                logger.info(f"\nType 2: TotalBsmtSF >= 3000")
                logger.info(f"Nombre d'outliers detectes: {len(bsmt_outliers)}")
                
                if method == 'contextual':
                    # Méthode contextuelle : utiliser le percentile 99 ou ajuster selon la corrélation
                    p99_bsmt = df['TotalBsmtSF'].quantile(0.99)
                    
                    for idx in bsmt_outliers.index:
                        old_bsmt = df.loc[idx, 'TotalBsmtSF']
                        
                        # Vérifier si c'est cohérent avec GrLivArea
                        if 'GrLivArea' in df.columns:
                            grliv = df.loc[idx, 'GrLivArea']
                            # Si TotalBsmtSF est beaucoup plus grand que GrLivArea, c'est suspect
                            if old_bsmt > grliv * 1.5:
                                # Probablement une erreur, utiliser le percentile 99
                                new_bsmt = min(p99_bsmt, grliv * 1.2)
                            else:
                                # Cohérent, utiliser percentile 99
                                new_bsmt = p99_bsmt
                        else:
                            new_bsmt = p99_bsmt
                        
                        df.loc[idx, 'TotalBsmtSF'] = new_bsmt
                        transformations_applied.append({
                            'index': idx,
                            'type': 'TotalBsmtSF',
                            'variable': 'TotalBsmtSF',
                            'old_value': old_bsmt,
                            'new_value': new_bsmt,
                            'method': 'contextual_capping'
                        })
                        logger.info(f"  Index {idx}: TotalBsmtSF ajuste de {old_bsmt:.0f} a {new_bsmt:.0f}")
                
                elif method == 'capping':
                    # Capping simple
                    p99_bsmt = df['TotalBsmtSF'].quantile(0.99)
                    for idx in bsmt_outliers.index:
                        old_bsmt = df.loc[idx, 'TotalBsmtSF']
                        df.loc[idx, 'TotalBsmtSF'] = p99_bsmt
                        transformations_applied.append({
                            'index': idx,
                            'type': 'TotalBsmtSF',
                            'variable': 'TotalBsmtSF',
                            'old_value': old_bsmt,
                            'new_value': p99_bsmt,
                            'method': 'capping'
                        })
                        logger.info(f"  Index {idx}: TotalBsmtSF ajuste de {old_bsmt:.0f} a {p99_bsmt:.0f}")
                
                elif method == 'winsorize':
                    # Winsorization : remplacer par les valeurs aux percentiles 1 et 99
                    p99_bsmt = df['TotalBsmtSF'].quantile(0.99)
                    for idx in bsmt_outliers.index:
                        old_bsmt = df.loc[idx, 'TotalBsmtSF']
                        df.loc[idx, 'TotalBsmtSF'] = p99_bsmt
                        transformations_applied.append({
                            'index': idx,
                            'type': 'TotalBsmtSF',
                            'variable': 'TotalBsmtSF',
                            'old_value': old_bsmt,
                            'new_value': p99_bsmt,
                            'method': 'winsorize'
                        })
        
        # Résumé des transformations
        if transformations_applied:
            logger.info("\n" + "=" * 80)
            logger.info("RESUME DES TRANSFORMATIONS:")
            logger.info("=" * 80)
            logger.info(f"Total de transformations appliquees: {len(transformations_applied)}")
            
            # Grouper par type
            by_type = {}
            for trans in transformations_applied:
                trans_type = trans['type']
                if trans_type not in by_type:
                    by_type[trans_type] = []
                by_type[trans_type].append(trans)
            
            for trans_type, trans_list in by_type.items():
                logger.info(f"\n  {trans_type}: {len(trans_list)} transformations")
            
            logger.info("\n" + "=" * 80)
            logger.info(f"Dataset final: {len(df)} observations (aucune suppression)")
            logger.info("=" * 80 + "\n")
        else:
            logger.info("\nAucun outlier detecte ou transforme.")
        
        return df
    
    def get_numeric_columns(self, df: pd.DataFrame) -> list:
        """Get list of numeric column names."""
        return df.select_dtypes(include=[np.number]).columns.tolist()
    
    def get_categorical_columns(self, df: pd.DataFrame) -> list:
        """Get list of categorical column names."""
        return df.select_dtypes(include=['object']).columns.tolist()


