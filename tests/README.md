# Tests MSPR-TPRE-601-ML

Ce répertoire contient tous les tests pour le système de prédiction COVID-19 utilisant Prophet.

## 📁 Structure des tests

```
tests/
├── __init__.py                 # Package de tests
├── conftest.py                 # Configuration pytest et fixtures
├── test_data_processing.py     # Tests de traitement des données
├── test_prophet_model.py       # Tests du modèle Prophet
├── test_database_operations.py # Tests des opérations de base de données
├── test_integration.py         # Tests d'intégration
├── test_performance.py         # Tests de performance
├── run_tests.py               # Script principal d'exécution
├── pytest.ini                # Configuration pytest
├── requirements-test.txt      # Dépendances de test
└── README.md                 # Cette documentation
```

## 🚀 Installation

### 1. Installer les dépendances de test

```bash
# Installer les dépendances de test
pip install -r tests/requirements-test.txt

# Ou utiliser le script d'installation automatique
python tests/run_tests.py --install-deps
```

### 2. Vérifier l'installation

```bash
# Vérifier que pytest fonctionne
python -m pytest --version

# Vérifier que tous les outils sont installés
python tests/run_tests.py --help
```

## 🧪 Types de tests

### Tests unitaires
- **Fichier**: `test_data_processing.py`
- **Objectif**: Tester les fonctions individuelles de traitement des données
- **Exécution**: `python tests/run_tests.py --unit`

### Tests du modèle Prophet
- **Fichier**: `test_prophet_model.py`
- **Objectif**: Tester l'entraînement, la prédiction et l'évaluation du modèle
- **Exécution**: `python tests/run_tests.py --prophet`

### Tests de base de données
- **Fichier**: `test_database_operations.py`
- **Objectif**: Tester les connexions et opérations de base de données
- **Exécution**: `python tests/run_tests.py --database`

### Tests d'intégration
- **Fichier**: `test_integration.py`
- **Objectif**: Tester le workflow complet du système
- **Exécution**: `python tests/run_tests.py --integration`

### Tests de performance
- **Fichier**: `test_performance.py`
- **Objectif**: Tester les performances et la scalabilité
- **Exécution**: `python tests/run_tests.py --performance`

## 🎯 Exécution des tests

### Script principal

Le script `run_tests.py` offre une interface unifiée pour exécuter tous les types de tests :

```bash
# Tous les tests
python tests/run_tests.py --all

# Tests spécifiques
python tests/run_tests.py --unit --verbose
python tests/run_tests.py --integration
python tests/run_tests.py --performance

# Avec couverture de code
python tests/run_tests.py --unit --coverage

# Générer un rapport HTML
python tests/run_tests.py --report
```

### Commandes pytest directes

```bash
# Tous les tests
python -m pytest tests/

# Tests spécifiques
python -m pytest tests/test_data_processing.py
python -m pytest tests/test_prophet_model.py

# Avec marqueurs
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m performance

# Avec couverture
python -m pytest --cov=. --cov-report=html

# Tests parallèles
python -m pytest -n auto
```

## 📊 Fixtures disponibles

### Données de test
- `sample_data`: DataFrame avec des données de test réalistes
- `sample_prophet_model`: Modèle Prophet entraîné pour les tests
- `sample_forecast`: Prédictions Prophet pour les tests
- `sample_metrics`: Métriques de performance simulées

### Environnement de test
- `temp_directories`: Répertoires temporaires pour les tests
- `mock_connection`: Connexion de base de données mockée
- `mock_environment_variables`: Variables d'environnement mockées

### Configuration
- `expected_columns`: Colonnes attendues dans les DataFrames
- `test_countries`: Liste de pays de test
- `mock_file_paths`: Chemins de fichiers mockés

## 🔧 Configuration

### pytest.ini
Configuration principale de pytest avec :
- Marqueurs personnalisés
- Options par défaut
- Filtres d'avertissements
- Configuration de couverture

### Variables d'environnement
Les tests utilisent des variables d'environnement mockées pour éviter les dépendances externes.

## 📈 Rapports et métriques

### Couverture de code
```bash
# Générer un rapport de couverture
python -m pytest --cov=. --cov-report=html --cov-report=term

# Rapport HTML dans htmlcov/
# Rapport terminal dans la console
```

### Rapport de tests HTML
```bash
# Générer un rapport HTML complet
python -m pytest --html=test_report.html --self-contained-html
```

### Métriques de performance
Les tests de performance génèrent automatiquement des métriques sur :
- Temps d'exécution
- Utilisation mémoire
- Scalabilité
- Performance des opérations

## 🐛 Débogage des tests

### Mode verbose
```bash
python tests/run_tests.py --unit --verbose
python -m pytest -v tests/
```

### Mode debug
```bash
python -m pytest --pdb tests/
```

### Tests spécifiques
```bash
# Test spécifique
python -m pytest tests/test_data_processing.py::TestDataProcessing::test_data_renaming

# Tests avec pattern
python -m pytest -k "data" tests/
```

## 🔒 Tests de sécurité

### Scan de sécurité
```bash
python tests/run_tests.py --security
```

### Vérification des types
```bash
python tests/run_tests.py --type-check
```

### Linting
```bash
python tests/run_tests.py --lint
```

## 📋 Bonnes pratiques

### Écriture de tests
1. **Nommage clair**: Utiliser des noms descriptifs pour les tests
2. **Isolation**: Chaque test doit être indépendant
3. **Fixtures**: Utiliser les fixtures pour la réutilisation
4. **Assertions**: Utiliser des assertions spécifiques et claires
5. **Documentation**: Documenter les tests complexes

### Organisation
1. **Structure**: Organiser les tests par fonctionnalité
2. **Marqueurs**: Utiliser les marqueurs pour catégoriser
3. **Fixtures**: Centraliser les fixtures communes
4. **Configuration**: Utiliser les fichiers de configuration

### Maintenance
1. **Mise à jour**: Maintenir les tests à jour avec le code
2. **Performance**: Surveiller les temps d'exécution
3. **Couverture**: Maintenir une couverture élevée
4. **Documentation**: Maintenir la documentation des tests

## 🚨 Dépannage

### Erreurs communes

#### ImportError
```bash
# Vérifier le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou utiliser pytest-pythonpath
python -m pytest --pythonpath=. tests/
```

#### Erreurs de base de données
- Les tests utilisent des mocks pour éviter les dépendances
- Vérifier que les fixtures sont correctement configurées

#### Erreurs de mémoire
- Les tests de performance peuvent être gourmands en mémoire
- Utiliser `--maxfail=1` pour arrêter au premier échec

### Logs et debug
```bash
# Activer les logs
python -m pytest --log-cli-level=DEBUG tests/

# Sauvegarder les logs
python -m pytest --log-file=test.log tests/
```

## 📞 Support

Pour toute question sur les tests :
1. Consulter cette documentation
2. Vérifier les logs d'erreur
3. Utiliser le mode verbose pour plus de détails
4. Consulter la documentation pytest officielle

## 🔄 Intégration continue

Les tests sont conçus pour s'intégrer facilement dans un pipeline CI/CD :

```yaml
# Exemple GitHub Actions
- name: Run tests
  run: |
    pip install -r tests/requirements-test.txt
    python tests/run_tests.py --all
```

```yaml
# Exemple GitLab CI
test:
  script:
    - pip install -r tests/requirements-test.txt
    - python tests/run_tests.py --all
``` 