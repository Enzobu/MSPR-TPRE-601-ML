# Procédures de Tests MSPR-TPRE-601-ML

## 📋 Table des matières

1. [Installation et configuration](#installation-et-configuration)
2. [Exécution des tests](#exécution-des-tests)
3. [Procédures par type de test](#procédures-par-type-de-test)
4. [Gestion des erreurs](#gestion-des-erreurs)
5. [Rapports et métriques](#rapports-et-métriques)
6. [Maintenance des tests](#maintenance-des-tests)
7. [Troubleshooting](#troubleshooting)

---

## 🛠️ Installation et configuration

### Prérequis système

#### Système d'exploitation
- **macOS** : 10.15+ (Catalina)
- **Linux** : Ubuntu 20.04+, CentOS 8+
- **Windows** : Windows 10+ (avec WSL recommandé)

#### Python
- **Version** : 3.8+
- **Gestionnaire** : pip ou conda
- **Environnement virtuel** : Recommandé

#### Base de données
- **PostgreSQL** : 13+
- **Extensions** : psycopg2-binary

### Installation des dépendances

#### 1. Clonage du projet
```bash
git clone <repository-url>
cd MSPR-TPRE-601-ML
```

#### 2. Création de l'environnement virtuel
```bash
# Avec venv (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Avec conda
conda create -n mspr-tests python=3.9
conda activate mspr-tests
```

#### 3. Installation des dépendances
```bash
# Dépendances principales
pip install -r requirements.txt

# Dépendances de test
pip install -r tests/requirements-test.txt

# Ou installation automatique
python tests/install_test_deps.py
```

#### 4. Configuration de l'environnement
```bash
# Variables d'environnement
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=mspr_test
export DB_USER=test_user
export DB_PASSWORD=test_password

# Ou création du fichier .env
cp .env.example .env
# Éditer .env avec vos paramètres
```

### Vérification de l'installation

#### Test rapide
```bash
python tests/test_quick.py
```

#### Vérification des outils
```bash
# pytest
pytest --version

# couverture
pytest --cov --version

# linting
pylint --version

# types
mypy --version
```

---

## 🚀 Exécution des tests

### Commandes de base

#### Tests unitaires uniquement
```bash
# Tous les tests unitaires
python tests/run_tests.py --unit

# Tests unitaires avec couverture
python tests/run_tests.py --unit --coverage

# Tests unitaires spécifiques
python tests/run_tests.py --unit --module data_processing
```

#### Tests d'intégration
```bash
# Tous les tests d'intégration
python tests/run_tests.py --integration

# Tests d'intégration avec base de données
python tests/run_tests.py --integration --db
```

#### Tests de performance
```bash
# Tests de performance
python tests/run_tests.py --performance

# Tests de performance avec métriques détaillées
python tests/run_tests.py --performance --detailed
```

#### Tests complets
```bash
# Tous les tests
python tests/run_tests.py --all

# Tests complets avec rapports
python tests/run_tests.py --all --reports
```

### Options avancées

#### Exécution parallèle
```bash
# Exécution en parallèle (4 processus)
python tests/run_tests.py --all --parallel 4
```

#### Filtrage des tests
```bash
# Tests par marqueur
python tests/run_tests.py --markers "slow"

# Tests par nom
python tests/run_tests.py --name "test_data"

# Tests par module
python tests/run_tests.py --module "prophet"
```

#### Génération de rapports
```bash
# Rapport HTML
python tests/run_tests.py --all --html-report

# Rapport JSON
python tests/run_tests.py --all --json-report

# Rapport XML (pour CI/CD)
python tests/run_tests.py --all --xml-report
```

---

## 🧪 Procédures par type de test

### Tests unitaires

#### Procédure standard
1. **Préparation** : Vérifier l'environnement
2. **Exécution** : Lancer les tests
3. **Validation** : Vérifier les résultats
4. **Documentation** : Enregistrer les résultats

```bash
# 1. Préparation
python tests/test_quick.py

# 2. Exécution
python tests/run_tests.py --unit --verbose

# 3. Validation
# Vérifier que tous les tests passent
# Vérifier la couverture de code

# 4. Documentation
# Les résultats sont automatiquement enregistrés
```

#### Tests de traitement des données
```bash
# Tests spécifiques aux données
python -m pytest tests/test_data_processing.py -v

# Tests avec données d'exemple
python -m pytest tests/test_data_processing.py::test_data_renaming -v
```

#### Tests du modèle Prophet
```bash
# Tests du modèle
python -m pytest tests/test_prophet_model.py -v

# Tests avec modèles pré-entraînés
python -m pytest tests/test_prophet_model.py::test_model_fitting -v
```

#### Tests de base de données
```bash
# Tests de base de données (avec mocks)
python -m pytest tests/test_database_operations.py -v

# Tests avec base réelle (optionnel)
python -m pytest tests/test_database_operations.py --db-real -v
```

### Tests d'intégration

#### Procédure standard
1. **Préparation** : Configurer l'environnement d'intégration
2. **Exécution** : Lancer les tests d'intégration
3. **Validation** : Vérifier les interactions
4. **Nettoyage** : Nettoyer les ressources

```bash
# 1. Préparation
# Vérifier la base de données de test
python tests/setup_integration_env.py

# 2. Exécution
python tests/run_tests.py --integration --verbose

# 3. Validation
# Vérifier les logs d'intégration
# Vérifier les données générées

# 4. Nettoyage
python tests/cleanup_integration_env.py
```

#### Tests de pipeline complet
```bash
# Test du pipeline de données
python -m pytest tests/test_integration.py::test_complete_data_pipeline -v

# Test du workflow d'entraînement
python -m pytest tests/test_integration.py::test_complete_model_training -v
```

### Tests de performance

#### Procédure standard
1. **Préparation** : Configurer l'environnement de performance
2. **Exécution** : Lancer les tests de performance
3. **Mesure** : Collecter les métriques
4. **Analyse** : Analyser les résultats

```bash
# 1. Préparation
# Vérifier les ressources système
python tests/check_performance_env.py

# 2. Exécution
python tests/run_tests.py --performance --detailed

# 3. Mesure
# Les métriques sont collectées automatiquement

# 4. Analyse
python tests/analyze_performance.py
```

#### Tests de temps d'exécution
```bash
# Test de performance d'entraînement
python -m pytest tests/test_performance.py::test_model_training_performance -v

# Test de performance de prédiction
python -m pytest tests/test_performance.py::test_prediction_performance -v
```

#### Tests de mémoire
```bash
# Test d'utilisation mémoire
python -m pytest tests/test_performance.py::test_memory_usage_performance -v

# Test de détection de fuites
python -m pytest tests/test_performance.py::test_memory_leak_detection -v
```

---

## ⚠️ Gestion des erreurs

### Types d'erreurs courantes

#### Erreurs d'installation
```bash
# Erreur : Module non trouvé
pip install -r tests/requirements-test.txt

# Erreur : Version incompatible
pip install --upgrade pytest

# Erreur : Permissions
sudo pip install -r tests/requirements-test.txt
```

#### Erreurs de configuration
```bash
# Erreur : Variables d'environnement manquantes
export DB_HOST=localhost
export DB_PORT=5432
# ... autres variables

# Erreur : Base de données inaccessible
# Vérifier que PostgreSQL est démarré
sudo systemctl start postgresql
```

#### Erreurs de test
```bash
# Erreur : Timeout
python tests/run_tests.py --timeout 300

# Erreur : Mémoire insuffisante
python tests/run_tests.py --memory-limit 1000

# Erreur : Tests flaky
python tests/run_tests.py --retry 3
```

### Procédures de débogage

#### Debug des tests unitaires
```bash
# Mode debug
python -m pytest tests/test_data_processing.py -v -s

# Debug avec pdb
python -m pytest tests/test_data_processing.py --pdb

# Debug avec breakpoint
# Ajouter breakpoint() dans le code de test
```

#### Debug des tests d'intégration
```bash
# Logs détaillés
python tests/run_tests.py --integration --log-level DEBUG

# Mode interactif
python tests/run_tests.py --integration --interactive
```

#### Debug des tests de performance
```bash
# Profiling détaillé
python tests/run_tests.py --performance --profile

# Analyse mémoire
python tests/run_tests.py --performance --memory-profile
```

### Procédures de récupération

#### Récupération après échec
```bash
# Nettoyage automatique
python tests/cleanup_after_failure.py

# Restauration de l'environnement
python tests/restore_test_env.py

# Relance des tests
python tests/run_tests.py --retry-failed
```

#### Récupération de base de données
```bash
# Sauvegarde avant test
python tests/backup_test_db.py

# Restauration après échec
python tests/restore_test_db.py
```

---

## 📊 Rapports et métriques

### Génération de rapports

#### Rapport de couverture
```bash
# Rapport HTML de couverture
python tests/run_tests.py --coverage --html-report

# Rapport XML pour CI/CD
python tests/run_tests.py --coverage --xml-report

# Rapport détaillé
python tests/run_tests.py --coverage --detailed-report
```

#### Rapport de performance
```bash
# Rapport de performance HTML
python tests/run_tests.py --performance --html-report

# Rapport JSON pour analyse
python tests/run_tests.py --performance --json-report

# Rapport comparatif
python tests/compare_performance.py
```

#### Rapport d'intégration
```bash
# Rapport d'intégration
python tests/run_tests.py --integration --html-report

# Rapport avec métriques
python tests/run_tests.py --integration --metrics-report
```

### Métriques collectées

#### Métriques de qualité
- **Couverture de code** : Pourcentage de code testé
- **Taux de succès** : Pourcentage de tests réussis
- **Temps d'exécution** : Durée totale des tests
- **Complexité cyclomatique** : Complexité du code

#### Métriques de performance
- **Temps d'entraînement** : Durée d'entraînement des modèles
- **Temps de prédiction** : Durée de génération des prédictions
- **Utilisation mémoire** : Consommation mémoire
- **Utilisation CPU** : Utilisation du processeur

#### Métriques de fiabilité
- **Tests flaky** : Tests instables
- **Taux d'échec** : Pourcentage d'échecs
- **Temps de récupération** : Temps de récupération après échec
- **Disponibilité** : Pourcentage de disponibilité

### Analyse des métriques

#### Analyse de tendances
```bash
# Analyse des tendances de performance
python tests/analyze_trends.py

# Analyse de la couverture
python tests/analyze_coverage.py

# Analyse des échecs
python tests/analyze_failures.py
```

#### Alertes et notifications
```bash
# Configuration des alertes
python tests/setup_alerts.py

# Test des alertes
python tests/test_alerts.py
```

---

## 🔧 Maintenance des tests

### Mise à jour des tests

#### Synchronisation avec le code
```bash
# Détection des changements
python tests/detect_changes.py

# Mise à jour automatique
python tests/update_tests.py

# Validation des mises à jour
python tests/validate_updates.py
```

#### Ajout de nouveaux tests
```bash
# Génération de template
python tests/generate_test_template.py --module new_module

# Validation du nouveau test
python tests/validate_new_test.py

# Intégration dans la suite
python tests/integrate_new_test.py
```

### Optimisation des tests

#### Optimisation de performance
```bash
# Analyse des tests lents
python tests/analyze_slow_tests.py

# Optimisation automatique
python tests/optimize_tests.py

# Validation des optimisations
python tests/validate_optimizations.py
```

#### Optimisation de maintenance
```bash
# Refactoring des tests
python tests/refactor_tests.py

# Simplification des fixtures
python tests/simplify_fixtures.py

# Documentation automatique
python tests/auto_document_tests.py
```

### Nettoyage et organisation

#### Nettoyage des données de test
```bash
# Nettoyage des fichiers temporaires
python tests/cleanup_temp_files.py

# Nettoyage de la base de données
python tests/cleanup_test_db.py

# Nettoyage des rapports anciens
python tests/cleanup_old_reports.py
```

#### Organisation des tests
```bash
# Réorganisation des tests
python tests/reorganize_tests.py

# Validation de l'organisation
python tests/validate_organization.py
```

---

## 🔍 Troubleshooting

### Problèmes courants

#### Tests qui échouent de manière intermittente
```bash
# Identification des tests flaky
python tests/identify_flaky_tests.py

# Correction des tests flaky
python tests/fix_flaky_tests.py

# Validation de la correction
python tests/validate_flaky_fix.py
```

#### Problèmes de performance
```bash
# Diagnostic de performance
python tests/diagnose_performance.py

# Optimisation automatique
python tests/auto_optimize.py

# Validation des optimisations
python tests/validate_optimizations.py
```

#### Problèmes de configuration
```bash
# Diagnostic de configuration
python tests/diagnose_config.py

# Correction automatique
python tests/auto_fix_config.py

# Validation de la configuration
python tests/validate_config.py
```

### Procédures d'escalade

#### Niveau 1 : Développeur
- Diagnostic initial
- Correction des problèmes simples
- Documentation des problèmes

#### Niveau 2 : Lead développeur
- Analyse approfondie
- Correction des problèmes complexes
- Optimisation des procédures

#### Niveau 3 : DevOps/Architecte
- Problèmes d'infrastructure
- Optimisations majeures
- Évolution de l'architecture

### Ressources de support

#### Documentation
- **README.md** : Guide principal
- **Troubleshooting.md** : Guide de dépannage
- **FAQ.md** : Questions fréquentes

#### Outils de diagnostic
- **Diagnostic automatique** : `python tests/diagnose.py`
- **Validation d'environnement** : `python tests/validate_env.py`
- **Test de connectivité** : `python tests/test_connectivity.py`

#### Contacts
- **Équipe de développement** : [Email]
- **DevOps** : [Email]
- **Support technique** : [Email]

---

*Ces procédures sont des guides pratiques qui doivent être adaptés aux besoins spécifiques de votre environnement et de votre équipe.* 