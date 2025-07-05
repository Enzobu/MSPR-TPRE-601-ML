# Guide de Dépannage - MSPR-TPRE-601-ML

Ce guide vous aidera à résoudre les problèmes courants rencontrés lors de l'utilisation du système de prédiction COVID-19.

## 🚨 Problèmes Fréquents

### 1. Erreurs de Connexion Base de Données

#### Problème : `psycopg2.OperationalError: connection to server failed`

**Causes possibles :**
- Fichier `.env` manquant ou mal configuré
- PostgreSQL non démarré
- Mauvaises credentials
- Firewall bloquant le port 5432

**Solutions :**

```bash
# 1. Vérifier le fichier .env
cat .env

# 2. Tester la connexion PostgreSQL
psql -h localhost -U your_user -d your_database

# 3. Vérifier le statut de PostgreSQL
sudo systemctl status postgresql

# 4. Redémarrer PostgreSQL
sudo systemctl restart postgresql

# 5. Vérifier les ports ouverts
netstat -tuln | grep 5432
```

#### Problème : `FATAL: password authentication failed`

**Solution :**
```bash
# Vérifier les credentials dans .env
export DB_PASSWORD="your_correct_password"

# Ou réinitialiser le mot de passe PostgreSQL
sudo -u postgres psql
ALTER USER your_user PASSWORD 'new_password';
```

### 2. Erreurs de Dépendances Python

#### Problème : `ModuleNotFoundError: No module named 'prophet'`

**Solutions :**
```bash
# 1. Réinstaller les dépendances
pip install -r requirements.txt

# 2. Vérifier l'environnement virtuel
which python
pip list | grep prophet

# 3. Installation manuelle si nécessaire
pip install prophet

# 4. Pour les problèmes de compilation
pip install prophet --no-cache-dir
```

#### Problème : `ImportError: cannot import name 'Prophet' from 'prophet'`

**Solution :**
```bash
# Désinstaller et réinstaller Prophet
pip uninstall prophet
pip install prophet

# Ou utiliser conda
conda install -c conda-forge prophet
```

### 3. Erreurs de Données

#### Problème : `ValueError: Trop peu de données pour [pays]`

**Causes :**
- Moins de 10 observations pour un pays
- Données manquantes ou corrompues
- Filtre trop restrictif

**Solutions :**
```python
# Vérifier les données par pays
SELECT country.name, COUNT(*) as nb_records
FROM statement 
JOIN country ON statement.id_country = country.id_country
WHERE statement.id_disease = 1
GROUP BY country.name
ORDER BY nb_records;

# Ajuster le seuil minimum si nécessaire
if len(df_country) < 5:  # Au lieu de 10
    continue
```

#### Problème : `KeyError: 'y'` ou `KeyError: 'ds'`

**Solution :**
```python
# Vérifier les colonnes disponibles
print(df.columns.tolist())

# Vérifier le renommage
df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
print(df.head())
```

### 4. Erreurs de Permissions

#### Problème : `PermissionError: [Errno 13] Permission denied`

**Solutions :**
```bash
# 1. Créer les dossiers avec les bonnes permissions
mkdir -p models predictions plots
chmod 755 models predictions plots

# 2. Vérifier les permissions actuelles
ls -la models/ predictions/ plots/

# 3. Corriger les permissions
sudo chown -R $USER:$USER models/ predictions/ plots/
```

### 5. Erreurs Docker

#### Problème : `docker: command not found`

**Solution :**
```bash
# Installation Docker sur Ubuntu
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
```

#### Problème : `docker build` échoue

**Solutions :**
```bash
# 1. Nettoyer Docker
docker system prune -a

# 2. Vérifier l'espace disque
df -h

# 3. Reconstruire sans cache
docker build --no-cache -t dev-mspr-601-ml .
```

#### Problème : Conteneur qui ne démarre pas

**Solutions :**
```bash
# 1. Vérifier les logs
docker logs dev_mspr_601_ml

# 2. Démarrer en mode interactif
docker run -it --rm dev-mspr-601-ml bash

# 3. Vérifier les variables d'environnement
docker exec -it dev_mspr_601_ml env
```

## 🔧 Diagnostics Approfondis

### Test de Connectivité Base de Données

```python
# Script de test : test_db.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=os.getenv("DB_PORT")
    )
    print("✅ Connexion réussie")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ Version PostgreSQL : {version[0]}")
    
    cur.execute("SELECT COUNT(*) FROM statement;")
    count = cur.fetchone()
    print(f"✅ Nombre d'enregistrements : {count[0]}")
    
except Exception as e:
    print(f"❌ Erreur : {e}")
```

### Vérification des Données

```sql
-- Requêtes de diagnostic
-- 1. Vérifier les tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- 2. Vérifier les données par pays
SELECT c.name, COUNT(*) as records, 
       MIN(s._date) as first_date, 
       MAX(s._date) as last_date
FROM statement s
JOIN country c ON s.id_country = c.id_country
WHERE s.id_disease = 1
GROUP BY c.name
ORDER BY records DESC;

-- 3. Vérifier les valeurs nulles
SELECT 
    COUNT(*) as total,
    COUNT(confirmed) as confirmed_not_null,
    COUNT(CASE WHEN confirmed > 0 THEN 1 END) as confirmed_positive
FROM statement 
WHERE id_disease = 1;
```

### Test des Composants

```bash
# Script de test complet : test_components.sh
#!/bin/bash

echo "🔍 Test des composants..."

# 1. Test Python
echo "1. Test Python:"
python --version

# 2. Test des dépendances
echo "2. Test des dépendances:"
python -c "import pandas, prophet, psycopg2; print('✅ Imports OK')"

# 3. Test des fichiers
echo "3. Test des fichiers:"
test -f .env && echo "✅ .env exists" || echo "❌ .env missing"
test -f query/query.sql && echo "✅ query.sql exists" || echo "❌ query.sql missing"

# 4. Test des dossiers
echo "4. Test des dossiers:"
test -d models && echo "✅ models/" || mkdir models && echo "✅ models/ created"
test -d predictions && echo "✅ predictions/" || mkdir predictions && echo "✅ predictions/ created"
test -d plots && echo "✅ plots/" || mkdir plots && echo "✅ plots/ created"

# 5. Test base de données
echo "5. Test base de données:"
python test_db.py

echo "🎉 Tests terminés"
```

## 📊 Monitoring et Logs

### Vérification des Logs

```bash
# 1. Logs d'exécution
tail -f etl.log

# 2. Logs système
journalctl -u postgresql -f

# 3. Logs Docker
docker logs dev_mspr_601_ml --follow
```

### Requêtes de Monitoring

```sql
-- 1. Vérifier les logs d'erreur
SELECT _date, error_string, COUNT(*) as nb_errors
FROM log 
WHERE is_success = false
GROUP BY _date, error_string
ORDER BY _date DESC;

-- 2. Métriques de performance
SELECT c.name, m.r2, m.rmse, m.mae, m._date
FROM metrics m
JOIN country c ON m.id_country = c.id_country
ORDER BY m._date DESC, m.r2 DESC;

-- 3. Dernières prédictions
SELECT c.name, COUNT(*) as nb_predictions, MAX(p.ds) as last_prediction
FROM prediction p
JOIN country c ON p.id_country = c.id_country
GROUP BY c.name
ORDER BY last_prediction DESC;
```

## 🛠️ Outils de Réparation

### Script de Nettoyage

```bash
#!/bin/bash
# cleanup.sh

echo "🧹 Nettoyage du système..."

# 1. Nettoyer les fichiers temporaires
rm -rf __pycache__/
rm -rf *.pyc
rm -rf .pytest_cache/

# 2. Nettoyer les sorties
rm -rf models/*
rm -rf predictions/*
rm -rf plots/*

# 3. Nettoyer Docker
docker system prune -f

# 4. Nettoyer les logs
truncate -s 0 etl.log

echo "✅ Nettoyage terminé"
```

### Script de Réinitialisation

```bash
#!/bin/bash
# reset.sh

echo "🔄 Réinitialisation du système..."

# 1. Arrêter les processus
docker stop dev_mspr_601_ml 2>/dev/null || true
docker rm dev_mspr_601_ml 2>/dev/null || true

# 2. Recréer l'environnement
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Recréer les dossiers
mkdir -p models predictions plots

# 4. Tester la configuration
python test_db.py

echo "✅ Réinitialisation terminée"
```

## 🚑 Récupération d'Urgence

### Sauvegarde des Données

```sql
-- Sauvegarde des tables importantes
COPY (SELECT * FROM metrics) TO '/tmp/metrics_backup.csv' WITH CSV HEADER;
COPY (SELECT * FROM log) TO '/tmp/log_backup.csv' WITH CSV HEADER;
COPY (SELECT * FROM prediction) TO '/tmp/prediction_backup.csv' WITH CSV HEADER;
```

### Restauration

```sql
-- Restauration des données
COPY metrics FROM '/tmp/metrics_backup.csv' WITH CSV HEADER;
COPY log FROM '/tmp/log_backup.csv' WITH CSV HEADER;
COPY prediction FROM '/tmp/prediction_backup.csv' WITH CSV HEADER;
```

## 📞 Support et Ressources

### Commandes Utiles

```bash
# Diagnostic rapide
python -c "import sys; print(sys.version)"
pip list | grep -E "(prophet|pandas|psycopg2)"
docker --version
psql --version

# Vérification des ressources
free -h              # Mémoire
df -h               # Espace disque
ps aux | grep python # Processus Python
```

### Contacts et Documentation

- **Documentation Prophet** : https://facebook.github.io/prophet/docs/
- **PostgreSQL** : https://www.postgresql.org/docs/
- **Docker** : https://docs.docker.com/
- **Pandas** : https://pandas.pydata.org/docs/

### FAQ

**Q : Le script est très lent, que faire ?**
R : Vérifiez les index de la base de données et limitez les pays traités pour les tests.

**Q : Les prédictions semblent incohérentes ?**
R : Vérifiez la qualité des données d'entrée et les métriques R² dans la table metrics.

**Q : Erreur de mémoire lors de l'exécution ?**
R : Augmentez la mémoire disponible ou traitez les pays par lots plus petits.

**Q : Les graphiques ne s'affichent pas ?**
R : Vérifiez que matplotlib est installé et que les permissions d'écriture sont correctes.

---

**Dernière mise à jour** : 19 décembre 2024  
**Version** : 1.0.0 