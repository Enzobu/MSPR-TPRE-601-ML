# MSPR-TPRE-601-ML : Système de Prédiction COVID-19 avec Prophet

## 📋 Vue d'ensemble

Ce projet implémente un système de prédiction des cas COVID-19 par pays utilisant le modèle Prophet de Facebook. Le système analyse les données historiques, génère des prédictions sur 90 jours, calcule des métriques de performance et stocke les résultats dans une base de données PostgreSQL.

### 🎯 Objectifs du projet

- **Prédiction temporelle** : Utiliser Prophet pour prédire l'évolution des cas COVID-19
- **Analyse par pays** : Traitement individualisé par pays avec données socio-économiques
- **Métriques de performance** : Calcul de RMSE, MAE, R2 pour évaluer la qualité des prédictions
- **Stockage persistant** : Sauvegarde des modèles, prédictions et métriques en base de données
- **Visualisation** : Génération automatique de graphiques de prédiction

## 🏗️ Architecture du système

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Base de       │    │   Traitement    │    │   Stockage      │
│   données       │───▶│   ML Prophet    │───▶│   Résultats     │
│   PostgreSQL    │    │   (main.py)     │    │   & Modèles     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   Évaluation    │    │   Fichiers      │
         │              │   Métriques     │    │   CSV/PKL/PNG   │
         │              └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Tables DB :   │
│   - statement   │
│   - country     │
│   - disease     │
│   - prediction  │
│   - metrics     │
│   - log         │
└─────────────────┘
```

## 📁 Structure du projet

```
MSPR-TPRE-601-ML/
├── 📄 main.py                  # Script principal de traitement ML
├── 📄 main.py.bak             # Sauvegarde de l'ancienne version
├── 📄 requirements.txt        # Dépendances Python
├── 📄 Dockerfile             # Configuration Docker
├── 📄 __init__.py            # Module Python
├── 📄 forecast_predictions.csv # Exemple de prédictions
├── 📄 prophet_model.pkl      # Modèle Prophet sauvegardé
├── 📄 java_opts.txt          # Options JVM pour Spark
├── 📄 py.sh                  # Script d'exécution interactive
├── 📄 pylint.sh              # Script de vérification code
├── 📂 bin/                   # Exécutables
│   └── py                    # Binaire Python
├── 📂 common/                # Modules communs
│   └── utils.py              # Utilitaires (lecture SQL)
├── 📂 db/                    # Connexion base de données
│   ├── __init__.py
│   └── connection.py         # Gestionnaire connexions PostgreSQL
├── 📂 query/                 # Requêtes SQL
│   └── query.sql             # Requête d'extraction des données
├── 📂 models/                # Modèles ML sauvegardés (généré)
├── 📂 predictions/           # Prédictions CSV (généré)
└── 📂 plots/                 # Graphiques PNG (généré)
```

## 🛠️ Installation et configuration

### Prérequis

- **Python 3.10+**
- **PostgreSQL 12+**
- **Docker** (optionnel)
- **Git**

### Installation locale

1. **Cloner le dépôt**
```bash
git clone <repository-url>
cd MSPR-TPRE-601-ML
```

2. **Créer un environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de la base de données**
Créer un fichier `.env` à la racine :
```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_DATABASE=your_database
DB_PORT=5432
```

### Installation Docker

1. **Construire l'image**
```bash
docker build -t dev-mspr-601-ml .
```

2. **Lancer le conteneur**
```bash
docker run --name dev_mspr_601_ml -v ./:/app -e PYTHONPATH=/app -d dev-mspr-601-ml
```

3. **Accéder au conteneur**
```bash
docker exec -it dev_mspr_601_ml bash
```

## 🗃️ Structure de la base de données

### Tables principales

#### `statement` - Données historiques COVID-19
```sql
- id_statement (PK)
- id_country (FK)
- id_disease (FK)
- _date (DATE)
- confirmed (INTEGER)
- deaths (INTEGER)
- recovered (INTEGER)
```

#### `country` - Informations pays
```sql
- id_country (PK)
- name (VARCHAR)
- population (BIGINT)
- pib (DECIMAL)
- continent (VARCHAR)
```

#### `disease` - Maladies référentielles
```sql
- id_disease (PK)
- name (VARCHAR)
- description (TEXT)
```

#### `prediction` - Prédictions générées
```sql
- id_prediction (PK)
- id_country (FK)
- id_disease (FK)
- ds (DATE)
- yhat (DECIMAL)
- yhat_lower (DECIMAL)
- yhat_upper (DECIMAL)
- trend (DECIMAL)
- [autres colonnes Prophet...]
```

#### `metrics` - Métriques d'évaluation
```sql
- id_metrics (PK)
- _date (DATE)
- RMSE (DECIMAL)
- MAE (DECIMAL)
- R2 (DECIMAL)
- id_country (FK)
- r2_bis (DECIMAL)    # R2 depuis 2022
- rmse_bis (DECIMAL)  # RMSE depuis 2022
- mae_bis (DECIMAL)   # MAE depuis 2022
```

#### `log` - Journalisation des exécutions
```sql
- id_log (PK)
- _date (DATE)
- is_success (BOOLEAN)
- error_string (TEXT)
- id_country (FK)
```

## 🚀 Utilisation

### Exécution manuelle

```bash
# Activation de l'environnement virtuel
source venv/bin/activate

# Exécution directe
python main.py

# Ou avec le script interactif
./py.sh
```

### Exécution avec Docker

```bash
# Dans le conteneur
docker exec -it dev_mspr_601_ml python /app/main.py

# Ou avec le script
docker exec -it dev_mspr_601_ml /app/py.sh
```

### Vérification du code

```bash
# Linting avec pylint
./pylint.sh

# Ou manuellement
pylint main.py
```

## 🔧 Détails techniques

### Algorithme Prophet

Le projet utilise **Facebook Prophet** pour la prédiction temporelle :

- **Modèle additif** : `y(t) = g(t) + s(t) + h(t) + ε(t)`
  - `g(t)` : Tendance (croissance)
  - `s(t)` : Saisonnalité
  - `h(t)` : Effets des jours fériés
  - `ε(t)` : Terme d'erreur

- **Régresseurs externes** :
  - `population` : Population normalisée du pays
  - `pib` : PIB normalisé du pays
  - `deaths` : Décès normalisés

### Processus de traitement

1. **Extraction des données** (`query.sql`)
   - Jointure des tables `statement`, `country`, `disease`
   - Normalisation des variables numériques
   - Filtrage COVID-19 (id_disease = 1)

2. **Préparation des données**
   - Renommage des colonnes pour Prophet (`ds`, `y`)
   - Suppression des valeurs nulles et négatives
   - Groupement par pays

3. **Entraînement du modèle**
   - Ajout des régresseurs externes
   - Entraînement Prophet par pays
   - Validation avec seuil minimum (10 observations)

4. **Génération des prédictions**
   - Horizon de 90 jours
   - Propagation des dernières valeurs des régresseurs
   - Contrainte de positivité (`clip(lower=0)`)

5. **Évaluation des performances**
   - **RMSE** : Racine de l'erreur quadratique moyenne
   - **MAE** : Erreur absolue moyenne
   - **R²** : Coefficient de détermination
   - Métriques spécifiques post-2022

6. **Sauvegarde des résultats**
   - Modèles Prophet (`.pkl`)
   - Prédictions (`.csv`)
   - Graphiques (`.png`)
   - Insertion en base de données

### Gestion des erreurs

Le système inclut une gestion robuste des erreurs :

- **Try-catch** par pays pour éviter l'arrêt complet
- **Logging** systématique dans la table `log`
- **Validation des données** avant traitement
- **Messages informatifs** pour le suivi d'exécution

## 📊 Métriques et performance

### Métriques calculées

1. **RMSE (Root Mean Square Error)**
   ```
   RMSE = √(Σ(y_pred - y_true)²/n)
   ```

2. **MAE (Mean Absolute Error)**
   ```
   MAE = Σ|y_pred - y_true|/n
   ```

3. **R² (Coefficient de détermination)**
   ```
   R² = 1 - (SS_res/SS_tot)
   ```

### Interprétation

- **R² proche de 1** : Excellent ajustement
- **R² autour de 0.5-0.8** : Ajustement correct
- **R² négatif** : Modèle moins bon que la moyenne
- **RMSE/MAE faibles** : Prédictions précises

## 🔐 Sécurité et bonnes pratiques

### Variables d'environnement

- **Jamais** de credentials en dur dans le code
- Utilisation de `.env` pour la configuration
- Variables chargées via `python-dotenv`

### Validation des données

- Vérification des types de données
- Gestion des valeurs nulles
- Contraintes de cohérence (valeurs positives)

### Logging

- Traçabilité complète des exécutions
- Stockage des erreurs pour debugging
- Horodatage des opérations

## 🐳 Déploiement

### Docker

Le `Dockerfile` inclut :
- **Base Python 3.10-slim**
- **Dépendances système** (PostgreSQL, build tools)
- **Pilote JDBC PostgreSQL**
- **Configuration d'environnement**

### Variables d'environnement Docker

```bash
docker run \
  -e DB_HOST=your-db-host \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-password \
  -e DB_DATABASE=your-database \
  -e DB_PORT=5432 \
  -e PYTHONPATH=/app \
  -v ./:/app \
  dev-mspr-601-ml
```

## 📝 Scripts utilitaires

### `py.sh` - Lanceur interactif

- Liste automatique des fichiers Python
- Exécution avec sélection numérique
- Mode batch avec paramètre
- Redirection des logs vers `etl.log`

### `pylint.sh` - Vérification qualité

- Analyse automatique de tous les fichiers Python
- Exclusion des `__init__.py`
- Rapport détaillé des problèmes de code

## 🧪 Tests et validation

### Validation des données

```python
# Vérification minimum de données
if len(df_country) < 10:
    raise ValueError(f"Trop peu de données pour {country}")

# Validation des valeurs
df = df[df['y'].notna()]
df = df[df['y'] > 0]
```

### Tests de cohérence

- Vérification de l'existence des pays en base
- Validation des ID de maladie
- Contrôle des types de données

## 📈 Monitoring et maintenance

### Fichiers de sortie

- **`models/`** : Modèles Prophet (`.pkl`)
- **`predictions/`** : Prédictions CSV
- **`plots/`** : Graphiques de prédiction
- **`etl.log`** : Logs d'exécution

### Surveillance

1. **Table `log`** : Suivi des succès/échecs
2. **Table `metrics`** : Évolution des performances
3. **Fichiers de sortie** : Vérification de la génération

### Maintenance recommandée

- **Nettoyage régulier** des prédictions obsolètes
- **Mise à jour des modèles** avec nouvelles données
- **Surveillance des métriques** de performance
- **Archivage des anciens logs**

## 🤝 Contribution

### Standards de code

- **PEP 8** : Style Python standard
- **Type hints** : Annotations de type
- **Docstrings** : Documentation des fonctions
- **Pylint** : Score minimum 8/10

### Processus de contribution

1. **Fork** du dépôt
2. **Branche** de fonctionnalité
3. **Tests** des modifications
4. **Pull request** avec description détaillée

## 📚 Dépendances

### Principales
- **pandas** : Manipulation de données
- **prophet** : Modèle de prédiction temporelle
- **psycopg2** : Connecteur PostgreSQL
- **scikit-learn** : Métriques d'évaluation
- **matplotlib** : Visualisation
- **joblib** : Sérialisation des modèles

### Développement
- **pylint** : Analyse de code
- **python-dotenv** : Gestion des variables d'environnement

## 🐛 Dépannage

### Erreurs communes

1. **Connexion DB** : Vérifier le fichier `.env`
2. **Dépendances** : Réinstaller `requirements.txt`
3. **Données insuffisantes** : Vérifier le seuil de 10 observations
4. **Permissions** : Vérifier les droits d'écriture des dossiers

### Logs de débogage

```bash
# Vérifier les logs
tail -f etl.log

# Logs Docker
docker logs dev_mspr_601_ml
```

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs d'exécution
2. Vérifier la table `log` en base
3. Examiner les métriques de performance
4. Contacter l'équipe de développement

---

**Version** : 1.0  
**Dernière mise à jour** : 2024  
**Équipe** : MSPR-TPRE-601-ML 