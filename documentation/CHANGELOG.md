# Changelog - MSPR-TPRE-601-ML

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### À venir
- Interface web pour visualisation des prédictions
- API REST pour accès aux données
- Parallélisation du traitement par pays
- Système de notifications par email
- Support multi-langues

## [1.0.0] - 2024-12-19

### Ajouté
- **Système de prédiction COVID-19** utilisant Prophet
- **Gestion par pays** avec régresseurs socio-économiques
- **Métriques de performance** : RMSE, MAE, R²
- **Logging robuste** avec gestion d'erreurs
- **Sauvegarde automatique** des modèles et prédictions
- **Visualisation** des graphiques de prédiction
- **Conteneurisation Docker** complète
- **Scripts utilitaires** pour l'exécution et la maintenance

### Fonctionnalités principales
- Traitement automatique des données historiques
- Entraînement de modèles Prophet par pays
- Prédictions sur 90 jours
- Calcul de métriques de performance
- Sauvegarde en base de données PostgreSQL
- Export des résultats (CSV, PNG, PKL)
- Gestion des erreurs et logging

### Composants techniques
- **Base de données** : PostgreSQL avec 6 tables
- **Modèle ML** : Facebook Prophet avec régresseurs externes
- **Métriques** : RMSE, MAE, R² (global et post-2022)
- **Conteneurisation** : Docker avec image Python 3.10
- **Dépendances** : 15 packages Python principaux

### Structure du projet
```
├── main.py                 # Script principal
├── db/connection.py        # Gestion connexions DB
├── common/utils.py         # Utilitaires
├── query/query.sql         # Requête d'extraction
├── Dockerfile             # Configuration Docker
├── requirements.txt       # Dépendances Python
├── py.sh                  # Script d'exécution
└── pylint.sh             # Vérification code
```

## [0.9.0] - 2024-12-15

### Ajouté
- Version initiale du système de prédiction
- Traitement des données COVID-19
- Modèle Prophet basique
- Connexion PostgreSQL

### Modifié
- Structure du projet
- Gestion des erreurs basique

## [0.8.0] - 2024-12-10

### Ajouté
- Scripts de base pour l'extraction de données
- Configuration Docker initiale
- Première version du modèle Prophet

### Problèmes connus
- Gestion d'erreurs limitée
- Pas de logging structuré
- Métriques de performance manquantes

## [0.5.0] - 2024-12-05

### Ajouté
- Structure initiale du projet
- Connexion base de données
- Première version du preprocessing

### Technique
- Python 3.10
- PostgreSQL 12+
- Prophet 1.1+

---

## Types de changements

- **Ajouté** : nouvelles fonctionnalités
- **Modifié** : modifications de fonctionnalités existantes
- **Déprécié** : fonctionnalités bientôt supprimées
- **Supprimé** : fonctionnalités supprimées
- **Corrigé** : corrections de bugs
- **Sécurité** : changements liés à la sécurité

## Guide de migration

### De 0.x vers 1.0.0

1. **Base de données** : Mettre à jour le schéma avec les nouvelles tables
2. **Configuration** : Migrer vers fichier `.env`
3. **Dépendances** : Réinstaller avec `pip install -r requirements.txt`
4. **Scripts** : Utiliser les nouveaux scripts `py.sh` et `pylint.sh`

### Changements incompatibles

- **Structure DB** : Nouvelles tables `metrics` et `log`
- **Configuration** : Variables d'environnement obligatoires
- **Sortie** : Nouveaux formats de fichiers de sortie

## Roadmap

### Version 1.1.0 (Q1 2025)
- [ ] Interface web avec dashboard
- [ ] API REST avec authentification
- [ ] Système de notifications
- [ ] Optimisations de performance

### Version 1.2.0 (Q2 2025)
- [ ] Support multi-maladies
- [ ] Modèles alternatifs (ARIMA, LSTM)
- [ ] Analyse de sensibilité
- [ ] Rapport automatique

### Version 2.0.0 (Q3 2025)
- [ ] Architecture microservices
- [ ] Traitement en temps réel
- [ ] Machine learning distribué
- [ ] Interface mobile

## Support des versions

| Version | Support | Fin de support |
|---------|---------|----------------|
| 1.0.x   | ✅ Actuel | 2025-12-31 |
| 0.9.x   | ⚠️ Maintenance | 2024-12-31 |
| 0.8.x   | ❌ Arrêté | 2024-10-31 |

## Contributeurs

- **Équipe MSPR-TPRE-601-ML** : Développement initial
- **Mainteneurs** : Équipe technique

## Licence

Ce projet est sous licence [MIT](LICENSE).

---

**Dernière mise à jour** : 19 décembre 2024 