# Architecture Technique - MSPR-TPRE-601-ML

## 🏗️ Vue d'ensemble de l'architecture

Le projet MSPR-TPRE-601-ML est une solution de machine learning pour la prédiction des cas COVID-19 basée sur une architecture modulaire et scalable.

## 🎯 Principaux Composants

### 1. **Couche de Données (Data Layer)**
- **Base de données PostgreSQL** : Stockage des données historiques et résultats
- **Requêtes SQL optimisées** : Extraction et transformation des données
- **Gestion des connexions** : Pool de connexions avec `psycopg2`

### 2. **Couche de Traitement (Processing Layer)**
- **Moteur Prophet** : Modèle de prédiction temporelle
- **Préprocessing** : Nettoyage et normalisation des données
- **Validation** : Contrôles de qualité et cohérence

### 3. **Couche de Persistance (Persistence Layer)**
- **Modèles sérialisés** : Sauvegarde des modèles Prophet (.pkl)
- **Prédictions** : Export des résultats en CSV
- **Visualisations** : Génération de graphiques PNG

### 4. **Couche de Monitoring (Monitoring Layer)**
- **Métriques de performance** : RMSE, MAE, R²
- **Journalisation** : Logs d'exécution et erreurs
- **Traçabilité** : Historique des opérations

## 🔧 Architecture Technique Détaillée

### Flux de Données

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                ARCHITECTURE MSPR-TPRE-601-ML                     │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │    │                 │
│  DONNÉES SOURCE │    │  PREPROCESSING  │    │  MODÉLISATION   │    │   RÉSULTATS     │
│                 │    │                 │    │                 │    │                 │
│  ┌─────────────┐│    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│  │statement    ││────┼─│Extraction   │ │────┼─│Prophet      │ │────┼─│Prédictions  │ │
│  │(historique) ││    │ │SQL          │ │    │ │Training     │ │    │ │CSV/PKL      │ │
│  └─────────────┘│    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │    │                 │
│  ┌─────────────┐│    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│  │country      ││────┼─│Normalisation│ │────┼─│Validation   │ │────┼─│Métriques    │ │
│  │(socio-éco)  ││    │ │& Cleaning   │ │    │ │& Evaluation │ │    │ │Performance  │ │
│  └─────────────┘│    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │    │                 │
│  ┌─────────────┐│    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│  │disease      ││────┼─│Filtering    │ │────┼─│Forecasting  │ │────┼─│Visualisation│ │
│  │(maladie)    ││    │ │& Grouping   │ │    │ │90 jours     │ │    │ │Graphiques   │ │
│  └─────────────┘│    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              COUCHE DE PERSISTANCE                               │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   PostgreSQL    │   Fichiers      │   Modèles       │      Monitoring         │
│   - prediction  │   - *.csv       │   - *.pkl       │   - logs/              │
│   - metrics     │   - *.png       │   - joblib      │   - metrics.db         │
│   - log         │   - exports     │   - serialized  │   - error_tracking     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## 🔄 Processus de Traitement

### 1. **Phase d'Initialisation**
```python
# Connexion à la base de données
conn = get_connection()

# Lecture de la requête SQL
query = utils.read_sql_query('./query/query.sql')

# Extraction des données
df = pd.read_sql_query(query, conn)
```

### 2. **Phase de Préprocessing**
```python
# Renommage des colonnes pour Prophet
df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})

# Nettoyage des données
df = df[df['y'].notna()]  # Suppression des valeurs nulles
df = df[df['y'] > 0]      # Suppression des valeurs négatives

# Sélection des colonnes nécessaires
colonnes_numeriques = ['population', 'pib', 'deaths']
df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques]
```

### 3. **Phase de Modélisation**
```python
# Traitement par pays
for country in df['country_name'].unique():
    df_country = df[df['country_name'] == country]
    
    # Validation des données
    if len(df_country) < 10:
        continue
    
    # Création et entraînement du modèle
    model = Prophet()
    for reg in colonnes_numeriques:
        model.add_regressor(reg)
    model.fit(df_country)
    
    # Génération des prédictions
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
```

### 4. **Phase d'Évaluation**
```python
# Calcul des métriques
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)

# Métriques spécifiques post-2022
df_eval_recent = df_eval[df_eval['ds'] >= pd.Timestamp("2022-01-01")]
r2_bis = r2_score(y_true_recent, y_pred_recent)
```

## 🗄️ Modèle de Données

### Schéma Relationnel

```sql
-- Table principale des pays
country (
    id_country [PK],
    name,
    population,
    pib,
    continent
)

-- Table des maladies
disease (
    id_disease [PK],
    name,
    description
)

-- Table des données historiques
statement (
    id_statement [PK],
    id_country [FK] → country.id_country,
    id_disease [FK] → disease.id_disease,
    _date,
    confirmed,
    deaths,
    recovered
)

-- Table des prédictions
prediction (
    id_prediction [PK],
    id_country [FK] → country.id_country,
    id_disease [FK] → disease.id_disease,
    ds,
    yhat,
    yhat_lower,
    yhat_upper,
    trend,
    [autres colonnes Prophet...]
)

-- Table des métriques
metrics (
    id_metrics [PK],
    _date,
    rmse,
    mae,
    r2,
    id_country [FK] → country.id_country,
    r2_bis,
    rmse_bis,
    mae_bis
)

-- Table de journalisation
log (
    id_log [PK],
    _date,
    is_success,
    error_string,
    id_country [FK] → country.id_country
)
```

### Relations et Contraintes

```sql
-- Contraintes de référence
ALTER TABLE statement ADD CONSTRAINT fk_statement_country 
    FOREIGN KEY (id_country) REFERENCES country(id_country);

ALTER TABLE statement ADD CONSTRAINT fk_statement_disease 
    FOREIGN KEY (id_disease) REFERENCES disease(id_disease);

-- Index pour les performances
CREATE INDEX idx_statement_date ON statement(_date);
CREATE INDEX idx_statement_country ON statement(id_country);
CREATE INDEX idx_prediction_date ON prediction(ds);
CREATE INDEX idx_metrics_date ON metrics(_date);
```

## 🚀 Modèle Prophet

### Configuration du Modèle

```python
# Paramètres par défaut
model = Prophet(
    growth='linear',              # Croissance linéaire
    seasonality_mode='additive',  # Saisonnalité additive
    yearly_seasonality=True,      # Saisonnalité annuelle
    weekly_seasonality=True,      # Saisonnalité hebdomadaire
    daily_seasonality=False,      # Pas de saisonnalité quotidienne
    interval_width=0.80          # Intervalle de confiance 80%
)

# Ajout des régresseurs externes
model.add_regressor('population')  # Population normalisée
model.add_regressor('pib')         # PIB normalisé
model.add_regressor('deaths')      # Décès normalisés
```

### Équation du Modèle

```
y(t) = g(t) + s(t) + h(t) + β×X(t) + ε(t)

Où :
- g(t) : Tendance (croissance)
- s(t) : Saisonnalité (annuelle, hebdomadaire)
- h(t) : Effets des jours fériés
- β×X(t) : Effet des régresseurs externes
- ε(t) : Terme d'erreur
```

### Régresseurs Externes

1. **Population** : Influence de la densité démographique
2. **PIB** : Impact socio-économique
3. **Deaths** : Corrélation avec la mortalité

## 🔧 Composants Modulaires

### 1. **Module de Connexion** (`db/connection.py`)
```python
def get_connection():
    """Gestionnaire de connexion PostgreSQL avec variables d'environnement"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=os.getenv("DB_PORT")
    )
```

### 2. **Module Utilitaires** (`common/utils.py`)
```python
def read_sql_query(filename):
    """Lecture des requêtes SQL depuis des fichiers"""
    with open(filename, 'r') as file:
        return file.read()
```

### 3. **Script Principal** (`main.py`)
- Orchestration du processus complet
- Gestion des erreurs et logging
- Traitement par pays
- Sauvegarde des résultats

## 🛡️ Sécurité et Robustesse

### Gestion des Erreurs

```python
try:
    # Traitement du pays
    model = Prophet()
    model.fit(df_country)
    log_success = True
    error_message = None
except Exception as e:
    # Gestion des erreurs
    log_success = False
    error_message = str(e)
    print(f"[ERROR] {country} -> {error_message}")
finally:
    # Logging systématique
    cur.execute("""
        INSERT INTO log (_date, is_success, error_string, id_country)
        VALUES (%s, %s, %s, %s)
    """, (today, log_success, error_message, id_country))
```

### Validation des Données

```python
# Validation minimum de données
if len(df_country) < 10:
    raise ValueError(f"Trop peu de données pour {country}")

# Validation des valeurs
df = df[df['y'].notna()]  # Pas de valeurs nulles
df = df[df['y'] > 0]      # Valeurs positives uniquement

# Contrainte de positivité des prédictions
forecast['yhat'] = forecast['yhat'].clip(lower=0)
```

## 📊 Monitoring et Métriques

### Métriques de Performance

1. **RMSE** : Erreur quadratique moyenne
2. **MAE** : Erreur absolue moyenne
3. **R²** : Coefficient de détermination
4. **Métriques temporelles** : Performance post-2022

### Système de Logging

```python
# Logging d'exécution
cur.execute("""
    INSERT INTO log (_date, is_success, error_string, id_country)
    VALUES (%s, %s, %s, %s)
""", (today, log_success, error_message, id_country))

# Logging des métriques
cur.execute("""
    INSERT INTO metrics (_date, RMSE, MAE, R2, id_country, r2_bis, rmse_bis, mae_bis)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (today, rmse, mae, r2, id_country, r2_bis, rmse_bis, mae_bis))
```

## 🐳 Conteneurisation

### Structure Docker

```dockerfile
FROM python:3.10-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    libpq-dev gcc build-essential

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configuration de l'environnement
WORKDIR /app
ENV PYTHONPATH=/app

# Téléchargement du driver PostgreSQL JDBC
RUN wget https://jdbc.postgresql.org/download/postgresql-42.6.0.jar
```

### Orchestration

```bash
# Construction
docker build -t dev-mspr-601-ml .

# Exécution
docker run --name dev_mspr_601_ml \
  -v ./:/app \
  -e PYTHONPATH=/app \
  --env-file .env \
  -d dev-mspr-601-ml
```

## 🔄 Évolutivité

### Améliorations Possibles

1. **Parallélisation** : Traitement multi-threaded par pays
2. **Microservices** : Séparation des composants
3. **Cache** : Redis pour les résultats fréquents
4. **API REST** : Exposition des prédictions
5. **Interface Web** : Dashboard de visualisation

### Scalabilité

```python
# Exemple de parallélisation
from concurrent.futures import ProcessPoolExecutor

def process_country(country_data):
    # Traitement d'un pays
    return train_and_predict(country_data)

# Traitement parallèle
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_country, countries_data))
```

## 📈 Performance

### Optimisations Actuelles

1. **Requêtes SQL optimisées** : Jointures efficaces
2. **Gestion mémoire** : Traitement par chunks
3. **Contraintes de données** : Validation précoce
4. **Sérialisation** : Modèles compacts avec joblib

### Métriques de Performance

- **Temps d'exécution** : ~2-5 minutes par pays
- **Utilisation mémoire** : ~500MB-1GB selon les données
- **Taille des modèles** : ~10-50MB par pays
- **Prédictions** : 90 jours en ~30 secondes

---

**Version** : 1.0  
**Dernière mise à jour** : 2024  
**Équipe** : MSPR-TPRE-601-ML 