# Le Kurtosis : Qu'est-ce que c'est et pourquoi c'est important ?

## Vue d'Ensemble

Le **kurtosis** (ou **kurtose** en français) est une mesure statistique qui décrit la forme d'une distribution, en particulier la "lourdeur" des queues de distribution par rapport à une distribution normale.

## 1. Définition du Kurtosis

### Mesure de la "Queue" de la Distribution

Le kurtosis mesure à quel point les valeurs extrêmes (outliers) sont présentes dans une distribution :

- **Kurtosis = 3** : Distribution normale (mésokurtique)
- **Kurtosis < 3** : Distribution avec des queues plus légères (platikurtique)
- **Kurtosis > 3** : Distribution avec des queues plus lourdes (leptokurtique)

### Formule

Le kurtosis est calculé comme suit :

```
Kurtosis = E[(X - μ)⁴] / σ⁴
```

Où :
- E est l'espérance mathématique
- μ est la moyenne
- σ est l'écart-type

## 2. Le Kurtosis de SalePrice dans notre Projet

### Valeur Observée

Dans notre dataset, la variable `SalePrice` présente un **kurtosis de 6.54**, ce qui est **très élevé**.

### Interprétation

Un kurtosis de 6.54 signifie que :

1. **Distribution leptokurtique** : La distribution a des queues beaucoup plus lourdes qu'une distribution normale
2. **Présence d'outliers** : Il y a plus de valeurs extrêmes (maisons très chères) que dans une distribution normale
3. **Pic plus pointu** : La distribution est plus concentrée autour de la moyenne que la distribution normale
4. **Risque pour les modèles** : Les valeurs extrêmes peuvent avoir un impact disproportionné sur les modèles de machine learning

### Comparaison avec la Distribution Normale

- **Distribution normale** : Kurtosis = 3
- **SalePrice** : Kurtosis = 6.54
- **Différence** : +3.54 (plus de 100% d'augmentation)

Cela indique que la distribution de `SalePrice` est **beaucoup plus "pointue"** et a des **queues beaucoup plus lourdes** qu'une distribution normale.

## 3. Pourquoi le Kurtosis est Important

### Impact sur les Modèles de Machine Learning

1. **Modèles linéaires** :
   - Supposent une distribution normale des erreurs
   - Un kurtosis élevé peut violer cette hypothèse
   - Peut affecter la validité des tests statistiques

2. **Sensibilité aux outliers** :
   - Un kurtosis élevé indique la présence de valeurs extrêmes
   - Ces valeurs peuvent "tirer" le modèle vers elles
   - Peut augmenter l'erreur de prédiction

3. **Stabilité des prédictions** :
   - Les modèles peuvent être instables avec des distributions leptokurtiques
   - Les prédictions peuvent être biaisées vers les valeurs extrêmes

### Relation avec la Skewness

- **Skewness** mesure l'**asymétrie** (à gauche ou à droite)
- **Kurtosis** mesure la **"lourdeur" des queues** (valeurs extrêmes)

Dans notre cas :
- **Skewness = 1.88** : Distribution asymétrique à droite
- **Kurtosis = 6.54** : Queues très lourdes (beaucoup de valeurs extrêmes)

Ces deux mesures indiquent que la distribution de `SalePrice` est **très éloignée de la normalité**.

## 4. Solutions pour Réduire le Kurtosis

### Transformation Logarithmique

La transformation logarithmique (`np.log1p()`) réduit à la fois la skewness et le kurtosis :

- **Avant transformation** :
  - Skewness = 1.88
  - Kurtosis = 6.54

- **Après transformation** :
  - Skewness ≈ 0.12 (quasi-normale)
  - Kurtosis ≈ 0.15 (quasi-normale)

### Autres Transformations Possibles

1. **Transformation Box-Cox** : Peut être plus efficace pour réduire le kurtosis
2. **Transformation Yeo-Johnson** : Alternative à Box-Cox qui fonctionne avec des valeurs négatives
3. **Suppression des outliers** : Peut réduire le kurtosis mais peut aussi réduire l'information

## 5. Interprétation dans le Contexte Immobilier

### Pourquoi le Kurtosis est Élevé ?

Dans le marché immobilier, il est normal d'avoir un kurtosis élevé car :

1. **Majorité des maisons** : Prix dans une plage "normale" (autour de $180,000)
2. **Quelques maisons de luxe** : Prix très élevés (jusqu'à $755,000)
3. **Distribution naturelle** : Le marché immobilier suit rarement une distribution normale

### Impact sur les Prédictions

- Les modèles doivent être capables de gérer ces valeurs extrêmes
- La transformation logarithmique aide à "aplatir" la distribution
- Les modèles basés sur les arbres (Random Forest, XGBoost) sont généralement plus robustes aux distributions non-normales

## 6. Conclusion

Le kurtosis de 6.54 pour `SalePrice` indique :

1. **Distribution très éloignée de la normalité**
2. **Présence importante de valeurs extrêmes**
3. **Nécessité d'une transformation** (logarithmique)
4. **Attention particulière aux outliers** lors de la modélisation

La transformation logarithmique est donc **essentielle** non seulement pour réduire la skewness, mais aussi pour normaliser le kurtosis et améliorer les performances des modèles.

