# Guide API et Utilisation - MSPR-TPRE-601-ML

## 🔧 Configuration et Initialisation

### 1. Fichier de configuration `.env`

```env
# Variables obligatoires
DB_HOST=localhost                # Adresse du serveur PostgreSQL
DB_USER=postgres                 # Nom d'utilisateur de la base de données
DB_PASSWORD=motdepasse          # Mot de passe de la base de données
DB_DATABASE=covid_predictions   # Nom de la base de données
DB_PORT=5432                    # Port PostgreSQL (par défaut : 5432)

# Variables optionnelles
PYTHONPATH=/app                 # Chemin Python (pour Docker)
LOG_LEVEL=INFO                  # Niveau de log (DEBUG, INFO, WARNING, ERROR)
```

### 2. Structure des tables requises

Avant d'exécuter le script, assurez-vous que votre base de données contient ces tables :

```sql
-- Table des pays
CREATE TABLE country (
    id_country SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    population BIGINT,
    pib DECIMAL(15,2),
    continent VARCHAR(50)
);

-- Table des maladies
CREATE TABLE disease (
    id_disease SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Table des données historiques
CREATE TABLE statement (
    id_statement SERIAL PRIMARY KEY,
    id_country INTEGER REFERENCES country(id_country),
    id_disease INTEGER REFERENCES disease(id_disease),
    _date DATE NOT NULL,
    confirmed INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    recovered INTEGER DEFAULT 0
);

-- Table des prédictions
CREATE TABLE prediction (
    id_prediction SERIAL PRIMARY KEY,
    id_country INTEGER REFERENCES country(id_country),
    id_disease INTEGER REFERENCES disease(id_disease),
    ds DATE NOT NULL,
    yhat DECIMAL(15,4),
    yhat_lower DECIMAL(15,4),
    yhat_upper DECIMAL(15,4),
    trend DECIMAL(15,4),
    trend_lower DECIMAL(15,4),
    trend_upper DECIMAL(15,4),
    deaths DECIMAL(15,4),
    deaths_lower DECIMAL(15,4),
    deaths_upper DECIMAL(15,4),
    pib DECIMAL(15,4),
    pib_lower DECIMAL(15,4),
    pib_upper DECIMAL(15,4),
    population DECIMAL(15,4),
    population_lower DECIMAL(15,4),
    population_upper DECIMAL(15,4)
);

-- Table des métriques
CREATE TABLE metrics (
    id_metrics SERIAL PRIMARY KEY,
    _date DATE NOT NULL,
    rmse DECIMAL(15,4),
    mae DECIMAL(15,4),
    r2 DECIMAL(15,4),
    id_country INTEGER REFERENCES country(id_country),
    r2_bis DECIMAL(15,4),
    rmse_bis DECIMAL(15,4),
    mae_bis DECIMAL(15,4)
);

-- Table des logs
CREATE TABLE log (
    id_log SERIAL PRIMARY KEY,
    _date DATE NOT NULL,
    is_success BOOLEAN NOT NULL,
    error_string TEXT,
    id_country INTEGER REFERENCES country(id_country)
);
```

## 📊 Utilisation du Script Principal

### 1. Exécution simple

```bash
# Activation de l'environnement virtuel
source venv/bin/activate

# Exécution du script
python main.py
```

### 2. Exécution avec Docker

```bash
# Construction de l'image
docker build -t dev-mspr-601-ml .

# Lancement du conteneur
docker run --name dev_mspr_601_ml \
  -v ./:/app \
  -e PYTHONPATH=/app \
  --env-file .env \
  -d dev-mspr-601-ml

# Exécution du script dans le conteneur
docker exec -it dev_mspr_601_ml python /app/main.py
```

### 3. Utilisation du script interactif

```bash
# Rendre le script exécutable
chmod +x py.sh

# Lancement interactif
./py.sh

# Ou directement avec un numéro de fichier
./py.sh 1  # Pour exécuter le premier fichier Python trouvé
```

## 🔍 Fonctionnalités Détaillées

### 1. Traitement des données

Le script effectue les opérations suivantes :

```python
# Lecture des données depuis la base
query = utils.read_sql_query('./query/query.sql')
df = pd.read_sql_query(query, conn)

# Préparation des données pour Prophet
df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
df = df[df['y'].notna()]  # Suppression des valeurs nulles
df = df[df['y'] > 0]      # Suppression des valeurs négatives
```

### 2. Entraînement du modèle Prophet

```python
# Création du modèle Prophet
model = Prophet()

# Ajout des régresseurs externes
for reg in ['population', 'pib', 'deaths']:
    model.add_regressor(reg)

# Entraînement
model.fit(df_country)
```

### 3. Génération des prédictions

```python
# Création du dataframe futur (90 jours)
future = model.make_future_dataframe(periods=90)

# Propagation des dernières valeurs des régresseurs
for col in ['population', 'pib', 'deaths']:
    future[col] = df_country[col].iloc[-1]

# Génération des prédictions
forecast = model.predict(future)
forecast['yhat'] = forecast['yhat'].clip(lower=0)  # Contrainte de positivité
```

## 📈 Métriques et Évaluation

### 1. Métriques calculées

Le système calcule automatiquement :

- **RMSE** : Racine de l'erreur quadratique moyenne
- **MAE** : Erreur absolue moyenne
- **R²** : Coefficient de détermination
- **Métriques spécifiques post-2022** : RMSE, MAE, R² sur les données récentes

### 2. Interprétation des résultats

```python
# Exemple d'interprétation
if r2 > 0.8:
    print("Excellent ajustement du modèle")
elif r2 > 0.5:
    print("Bon ajustement du modèle")
elif r2 > 0.0:
    print("Ajustement faible du modèle")
else:
    print("Modèle peu fiable")
```

## 📁 Fichiers de Sortie

### 1. Modèles sauvegardés

```bash
models/
├── prophet_model_France.pkl
├── prophet_model_Germany.pkl
├── prophet_model_Italy.pkl
└── ...
```

### 2. Prédictions CSV

```bash
predictions/
├── forecast_France.csv
├── forecast_Germany.csv
├── forecast_Italy.csv
└── ...
```

Structure des fichiers CSV :
```csv
ds,yhat,yhat_lower,yhat_upper,trend,trend_lower,trend_upper,deaths,pib,population
2024-01-01,12345.67,11000.00,13500.00,12000.00,11800.00,12200.00,0.25,0.45,0.78
...
```

### 3. Graphiques de prédiction

```bash
plots/
├── forecast_plot_France.png
├── forecast_plot_Germany.png
├── forecast_plot_Italy.png
└── ...
```

## 🔧 Personnalisation et Extensions

### 1. Modification des paramètres Prophet

```python
# Personnalisation du modèle
model = Prophet(
    growth='linear',           # Type de croissance
    seasonality_mode='additive',  # Mode saisonnalité
    yearly_seasonality=True,   # Saisonnalité annuelle
    weekly_seasonality=True,   # Saisonnalité hebdomadaire
    daily_seasonality=False,   # Saisonnalité quotidienne
    interval_width=0.80       # Intervalle de confiance
)
```

### 2. Ajout de nouveaux régresseurs

```python
# Ajout d'un nouveau régresseur
model.add_regressor('temperature')  # Exemple : température
model.add_regressor('vaccination_rate')  # Exemple : taux de vaccination
```

### 3. Modification de l'horizon de prédiction

```python
# Changer l'horizon de prédiction
future = model.make_future_dataframe(periods=30)   # 30 jours
future = model.make_future_dataframe(periods=365)  # 1 an
```

## 🐛 Gestion des Erreurs

### 1. Erreurs communes et solutions

| Erreur | Cause | Solution |
|--------|-------|----------|
| `psycopg2.OperationalError` | Connexion DB échouée | Vérifier `.env` et connectivité |
| `ValueError: Trop peu de données` | < 10 observations | Augmenter les données historiques |
| `ImportError` | Dépendance manquante | `pip install -r requirements.txt` |
| `PermissionError` | Droits d'écriture | `chmod 755` sur les dossiers |

### 2. Logs et débogage

```bash
# Consultation des logs
tail -f etl.log

# Vérification des erreurs en base
SELECT * FROM log WHERE is_success = false ORDER BY _date DESC;

# Vérification des métriques
SELECT country.name, metrics.* 
FROM metrics 
JOIN country ON metrics.id_country = country.id_country 
ORDER BY _date DESC;
```

## 📋 Checklist de Validation

### Avant l'exécution
- [ ] Fichier `.env` configuré
- [ ] Base de données accessible
- [ ] Tables créées et données présentes
- [ ] Dépendances installées
- [ ] Dossiers de sortie créés

### Après l'exécution
- [ ] Logs sans erreur critique
- [ ] Modèles générés dans `models/`
- [ ] Prédictions dans `predictions/`
- [ ] Graphiques dans `plots/`
- [ ] Métriques en base de données
- [ ] Logs d'exécution en base

## 🚀 Optimisations Possibles

### 1. Performance
- Parallélisation du traitement par pays
- Optimisation des requêtes SQL
- Utilisation de chunks pour les gros datasets

### 2. Fonctionnalités
- Interface web pour visualisation
- API REST pour accès aux prédictions
- Notifications automatiques d'échecs
- Système de cache pour les résultats

### 3. Monitoring
- Métriques Prometheus
- Dashboards Grafana
- Alertes automatiques
- Historique des performances

## 📞 Support et Maintenance

### Commandes utiles

```bash
# Vérification de l'état du système
docker ps -a                    # État des conteneurs
docker logs dev_mspr_601_ml     # Logs du conteneur
python -m pip list            # Dépendances installées
pylint main.py                # Qualité du code

# Nettoyage
docker system prune -a         # Nettoyage Docker
rm -rf models/* predictions/* plots/*  # Nettoyage des sortiesww
```

### Contact et ressources

- **Documentation Prophet** : https://facebook.github.io/prophet/
- **PostgreSQL** : https://www.postgresql.org/docs/
- **Pandas** : https://pandas.pydata.org/docs/
- **Scikit-learn** : https://scikit-learn.org/stable/

---

**Version** : 1.0  
**Dernière mise à jour** : 2024  
**Équipe** : MSPR-TPRE-601-ML 