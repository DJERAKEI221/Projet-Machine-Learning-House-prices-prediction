# Sélection Objective des Variables pour le Modèle

Ce document synthétise les analyses statistiques (corrélation pour les variables quantitatives et ANOVA pour les variables qualitatives) pour recommander objectivement les variables à intégrer dans le modèle de prédiction des prix immobiliers.

---

## 1. Variables Quantitatives (Analyse de Corrélation)

### Variables Fortement Corrélées avec SalePrice (|r| > 0.5)

Les variables suivantes présentent une corrélation **modérée à forte** avec le prix de vente :

| Variable | Corrélation (|r|) | Niveau | Recommandation |
|----------|-------------------|--------|----------------|
| OverallQual | 0.798 | Très forte | **OUI** |
| GrLivArea | 0.736 | Forte | **OUI** |
| TotalBsmtSF | 0.653 | Forte | **OUI** |
| GarageCars | 0.640 | Forte | **OUI** |
| 1stFlrSF | 0.635 | Forte | **OUI - Priorité 2** |
| GarageArea | 0.634 | Forte | **OUI - Priorité 2** |
| FullBath | 0.564 | Modérée-Forte | **OUI - Priorité 2** |
| TotRmsAbvGrd | 0.544 | Modérée-Forte | **OUI - Priorité 2** |
| YearBuilt | 0.525 | Modérée-Forte | **OUI - Priorité 2** |
| YearRemodAdd | 0.509 | Modérée-Forte | **OUI - Priorité 2** |

**Total : 10 variables quantitatives à intégrer**

---

## 2. Variables Qualitatives (Tests ANOVA)

### Variables Qualitatives Significatives (p < 0.05, ordre par η²)

| Variable | η² (Taille effet) | p-value | F-stat | Recommandation |
|----------|-------------------|---------|--------|----------------|
| Neighborhood | 0.5318 | 2.55e-216 | 67.90 | **OUI** |
| ExterQual | 0.4926 | 6.77e-214 | 471.16 | **OUI** |
| BsmtQual | 0.4754 | 5.50e-202 | 329.58 | **OUI** |
| KitchenQual | 0.4673 | 1.54e-198 | 425.78 | **OUI** |
| GarageFinish | 0.3083 | 4.82e-116 | 216.33 | **OUI** |
| FireplaceQu | 0.2950 | 1.05e-107 | 121.67 | **OUI - Priorité 2** |
| Foundation | 0.2578 | 1.48e-91 | 100.99 | **OUI - Priorité 2** |
| GarageType | 0.2510 | 1.06e-87 | 81.17 | **OUI - Priorité 2** |
| BsmtFinType1 | 0.2141 | 1.19e-72 | 65.97 | **OUI - Priorité 2** |
| HeatingQC | 0.1958 | 1.87e-68 | 118.11 | **OUI - Priorité 2** |
| MasVnrType | 0.1906 | 1.80e-66 | 114.31 | **OUI - Priorité 2** |
| BsmtExposure | 0.1564 | 2.07e-52 | 67.45 | **OUI - Priorité 3** |
| SaleCondition | 0.1443 | 4.99e-47 | 49.05 | **OUI - Priorité 3** |
| SaleType | 0.1464 | 2.72e-45 | 31.11 | **OUI - Priorité 3** |
| Exterior1st | 0.1510 | 1.33e-44 | 23.36 | **OUI - Priorité 3** |
| Exterior2nd | 0.1509 | 2.94e-43 | 19.75 | **OUI - Priorité 3** |
| MSZoning | 0.1072 | 1.22e-34 | 43.66 | **OUI - Priorité 3** |
| LotShape | 0.0796 | 5.01e-26 | 41.99 | **OUI - Priorité 3** |
| HouseStyle | 0.0885 | 6.43e-26 | 20.13 | **OUI - Priorité 3** |
| GarageQual | 0.0810 | 7.51e-25 | 25.63 | **OUI - Priorité 3** |

**Total : 20 variables qualitatives significatives à intégrer**

---

## 3. Critères de Sélection Objectifs

### Seuils Statistiques Utilisés

#### Variables Quantitatives :
- **Seuil de corrélation** : |r| > 0.5 (corrélation modérée à forte)
- **Justification** : Une corrélation de 0.5 explique 25% de la variance (r² = 0.25)

#### Variables Qualitatives :
- **Seuil de significativité** : p-value < 0.05 (niveau de confiance 95%)
- **Seuil de taille d'effet** : Toutes les variables significatives (η² variable)
- **Justification** : p < 0.05 indique que l'effet observé n'est pas dû au hasard

### Classification par Priorité

#### Variables Essentielles (Impact Très Élevé)
- **Quantitatives** : Corrélation |r| ≥ 0.65
- **Qualitatives** : η² ≥ 0.30 (explique ≥ 30% de la variance)

#### Priorité 2 - Variables Importantes (Impact Élevé)
- **Quantitatives** : Corrélation 0.50 ≤ |r| < 0.65
- **Qualitatives** : η² entre 0.15 et 0.30

#### Priorité 3 - Variables Utiles (Impact Modéré mais Significatif)
- **Quantitatives** : Peu applicables (toutes > 0.5 sont essentielles ou importantes)
- **Qualitatives** : η² < 0.15 mais p < 0.05

---

## 4. Recommandations Finales

### Variables à Intégrer ABSOLUMENT

#### Variables Quantitatives (4 variables) :
1. **OverallQual** (r = 0.798)
2. **GrLivArea** (r = 0.736)
3. **TotalBsmtSF** (r = 0.653)
4. **GarageCars** (r = 0.640)

#### Variables Qualitatives (5 variables) :
1. **Neighborhood** (η² = 0.532)
2. **ExterQual** (η² = 0.493)
3. **BsmtQual** (η² = 0.475)
4. **KitchenQual** (η² = 0.467)
5. **GarageFinish** (η² = 0.308)

**Total : 9 variables**

---

### Variables à Intégrer (Priorité 2)

#### Variables Quantitatives (6 variables) :
1. **1stFlrSF** (r = 0.635)
2. **GarageArea** (r = 0.634)
3. **FullBath** (r = 0.564)
4. **TotRmsAbvGrd** (r = 0.544)
5. **YearBuilt** (r = 0.525)
6. **YearRemodAdd** (r = 0.509)

#### Variables Qualitatives (5 variables) :
1. **FireplaceQu** (η² = 0.295)
2. **Foundation** (η² = 0.258)
3. **GarageType** (η² = 0.251)
4. **BsmtFinType1** (η² = 0.214)
5. **HeatingQC** (η² = 0.196)
6. **MasVnrType** (η² = 0.191)

**Total Priorité 2 : 12 variables**

---

### Variables à Considérer (Priorité 3)

#### Variables Qualitatives (9 variables) :
1. **BsmtExposure** (η² = 0.156)
2. **SaleCondition** (η² = 0.144)
3. **SaleType** (η² = 0.146)
4. **Exterior1st** (η² = 0.151)
5. **Exterior2nd** (η² = 0.151)
6. **MSZoning** (η² = 0.107)
7. **HouseStyle** (η² = 0.089)
8. **LotShape** (η² = 0.080)
9. **GarageQual** (η² = 0.081)

**Total Priorité 3 : 9 variables**

---

## 5. Résumé Global

### Total des Variables Recommandées

| Catégorie | Essentielles | Importantes | Utiles | **TOTAL** |
|-----------|--------------|-------------|--------|-----------|
| **Quantitatives** | 4 | 6 | 0 | **10** |
| **Qualitatives** | 5 | 6 | 9 | **20** |
| **TOTAL** | **9** | **12** | **9** | **30** |

### Recommandation Stratégique

#### Modele
- **9 variables** : 4 quantitatives + 5 qualitatives
- **Avantage** : Modèle simple, interprétable, avec les variables les plus importantes
- **Recommandé pour** : Modèles de base, interprétation métier

#### Modèle Standard (Variables Essentielles + Variables Importantes)
- **21 variables** : 10 quantitatives + 11 qualitatives
- **Avantage** : Équilibre entre performance et complexité
- **Recommandé pour** : Modèles de production, meilleur compromis

#### Modèle Complet (Toutes les priorités)
- **30 variables** : 10 quantitatives + 20 qualitatives
- **Avantage** : Performance maximale possible
- **Recommandé pour** : Optimisation finale, compétitions Kaggle

---

## 6. Notes Importantes

### Gestion de la Multicolinéarité

Certaines variables sont fortement corrélées entre elles :
- **GarageCars** et **GarageArea** (r = 0.882) : Conserver les deux ou choisir une seule
- **TotalBsmtSF** et **1stFlrSF** (r = 0.795) : Conserver les deux (information complémentaire)
- **GrLivArea** et **TotRmsAbvGrd** (r = 0.825) : Conserver les deux

**Recommandation** : Utiliser la régularisation (L1/L2) pour gérer automatiquement la multicolinéarité, ou utiliser des algorithmes robustes (Random Forest, XGBoost, LightGBM).

### Encodage des Variables Qualitatives

#### Variables Ordinales (encodage ordinal recommandé) :
- ExterQual, BsmtQual, KitchenQual, HeatingQC, FireplaceQu, GarageQual, GarageFinish

#### Variables Nominales (one-hot encoding ou label encoding) :
- Neighborhood, Foundation, GarageType, BsmtFinType1, MasVnrType, BsmtExposure, SaleCondition, SaleType, Exterior1st, Exterior2nd, MSZoning, LotShape, HouseStyle

---

## 7. Conclusion

Basé sur les analyses statistiques objectives :

1. **10 variables quantitatives** doivent être intégrées (corrélation |r| > 0.5)
2. **20 variables qualitatives** doivent être intégrées (ANOVA p < 0.05)
3. **Total recommandé : 30 variables** pour un modèle complet

**Recommandation principale** : Commencer par le **modèle standard (21 variables)** qui offre le meilleur équilibre entre performance et complexité, puis ajuster selon les besoins (ajouter ou retirer des variables utiles selon les performances du modèle).
