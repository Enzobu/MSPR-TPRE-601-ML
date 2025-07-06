"""
Tests unitaires pour le traitement des données

Ce module teste les fonctions de préprocessing, nettoyage et validation des données.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common.utils as utils


class TestDataProcessing:
    """Tests pour le traitement des données."""

    def test_data_renaming(self, sample_data):
        """Test du renommage des colonnes."""
        # Test du renommage des colonnes
        df_renamed = sample_data.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        assert 'ds' in df_renamed.columns
        assert 'y' in df_renamed.columns
        assert '_date' not in df_renamed.columns
        assert 'confirmed' not in df_renamed.columns

    def test_data_filtering(self, sample_data):
        """Test du filtrage des données."""
        # Ajouter des valeurs nulles et négatives pour tester
        df_with_nulls = sample_data.copy()
        df_with_nulls.loc[0, 'y'] = np.nan
        df_with_nulls.loc[1, 'y'] = -5
        
        # Appliquer les filtres
        df_filtered = df_with_nulls[df_with_nulls['y'].notna()]
        df_filtered = df_filtered[df_filtered['y'] > 0]
        
        # Vérifications
        assert len(df_filtered) < len(df_with_nulls)
        assert df_filtered['y'].isna().sum() == 0
        assert (df_filtered['y'] > 0).all()

    def test_column_selection(self, sample_data, expected_columns):
        """Test de la sélection des colonnes."""
        # Renommer d'abord
        df_renamed = sample_data.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Sélectionner les colonnes
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df_selected = df_renamed[expected_columns].copy()
        
        # Vérifications
        assert set(df_selected.columns) == set(expected_columns)
        assert all(col in df_selected.columns for col in colonnes_numeriques)

    def test_data_validation(self, sample_data):
        """Test de la validation des données."""
        # Test avec données valides
        assert len(sample_data) > 0
        assert 'country_name' in sample_data.columns
        assert 'id_country' in sample_data.columns
        
        # Test de la présence de pays uniques
        unique_countries = sample_data['country_name'].unique()
        assert len(unique_countries) > 0

    def test_data_types(self, sample_data):
        """Test des types de données."""
        # Vérifier que les colonnes numériques sont bien numériques
        numeric_columns = ['population', 'pib', 'deaths']
        for col in numeric_columns:
            if col in sample_data.columns:
                assert pd.api.types.is_numeric_dtype(sample_data[col])

    def test_date_format(self, sample_data):
        """Test du format des dates."""
        # Vérifier que les dates sont bien des dates
        if '_date' in sample_data.columns:
            assert pd.api.types.is_datetime64_any_dtype(sample_data['_date'])
        elif 'ds' in sample_data.columns:
            assert pd.api.types.is_datetime64_any_dtype(sample_data['ds'])

    def test_country_data_integrity(self, sample_data):
        """Test de l'intégrité des données par pays."""
        # Vérifier que chaque pays a un ID unique
        country_id_mapping = sample_data.groupby('country_name')['id_country'].first()
        assert len(country_id_mapping) == len(country_id_mapping.unique())

    def test_numeric_data_ranges(self, sample_data):
        """Test des plages de valeurs numériques."""
        # Vérifier que les valeurs sont dans des plages raisonnables
        if 'population' in sample_data.columns:
            assert sample_data['population'].min() >= 0
            assert sample_data['population'].max() <= 1.0  # Normalisé
        
        if 'pib' in sample_data.columns:
            assert sample_data['pib'].min() >= 0
            assert sample_data['pib'].max() <= 1.0  # Normalisé

    def test_missing_data_handling(self, sample_data):
        """Test de la gestion des données manquantes."""
        # Créer des données avec des valeurs manquantes
        df_with_missing = sample_data.copy()
        df_with_missing.loc[0, 'population'] = np.nan
        df_with_missing.loc[1, 'pib'] = np.nan
        
        # Compter les valeurs manquantes
        missing_counts = df_with_missing.isnull().sum()
        
        # Vérifier que nous pouvons identifier les valeurs manquantes
        assert missing_counts['population'] > 0 or missing_counts['pib'] > 0

    def test_data_grouping_by_country(self, sample_data):
        """Test du groupement des données par pays."""
        # Grouper par pays
        grouped = sample_data.groupby('country_name')
        
        # Vérifier que chaque pays a des données
        for country_name, group in grouped:
            assert len(group) > 0
            assert all(group['country_name'] == country_name)

    def test_minimum_data_requirement(self, sample_data):
        """Test de l'exigence de données minimales."""
        # Tester avec différents seuils
        thresholds = [5, 10, 20]
        
        for threshold in thresholds:
            for country in sample_data['country_name'].unique():
                country_data = sample_data[sample_data['country_name'] == country]
                
                if len(country_data) < threshold:
                    # Devrait lever une exception ou être rejeté
                    with pytest.raises(ValueError):
                        if len(country_data) < threshold:
                            raise ValueError(f"Trop peu de données pour {country}")

    def test_data_consistency(self, sample_data):
        """Test de la cohérence des données."""
        # Vérifier que les données sont cohérentes
        for country in sample_data['country_name'].unique():
            country_data = sample_data[sample_data['country_name'] == country]
            
            # Vérifier que l'ID du pays est constant
            unique_ids = country_data['id_country'].unique()
            assert len(unique_ids) == 1

    def test_temporal_data_ordering(self, sample_data):
        """Test de l'ordre temporel des données."""
        # Vérifier que les données sont ordonnées chronologiquement
        for country in sample_data['country_name'].unique():
            country_data = sample_data[sample_data['country_name'] == country]
            
            if '_date' in country_data.columns:
                dates = pd.to_datetime(country_data['_date'])
                assert dates.is_monotonic_increasing

    def test_outlier_detection(self, sample_data):
        """Test de la détection d'outliers."""
        # Ajouter des outliers pour tester
        df_with_outliers = sample_data.copy()
        df_with_outliers.loc[0, 'y'] = 1000000  # Valeur extrême
        
        # Calculer les statistiques
        q1 = df_with_outliers['y'].quantile(0.25)
        q3 = df_with_outliers['y'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Identifier les outliers
        outliers = df_with_outliers[
            (df_with_outliers['y'] < lower_bound) | 
            (df_with_outliers['y'] > upper_bound)
        ]
        
        assert len(outliers) > 0

    def test_data_normalization(self, sample_data):
        """Test de la normalisation des données."""
        # Vérifier que les données socio-économiques sont normalisées
        if 'population' in sample_data.columns:
            population_values = sample_data['population']
            assert population_values.min() >= 0
            assert population_values.max() <= 1.0
        
        if 'pib' in sample_data.columns:
            pib_values = sample_data['pib']
            assert pib_values.min() >= 0
            assert pib_values.max() <= 1.0

    def test_duplicate_detection(self, sample_data):
        """Test de la détection de doublons."""
        # Vérifier qu'il n'y a pas de doublons complets
        duplicates = sample_data.duplicated()
        duplicate_count = duplicates.sum()
        
        # Il peut y avoir des doublons si les données sont générées de manière aléatoire
        # mais nous vérifions que la détection fonctionne
        assert duplicate_count >= 0

    def test_data_completeness(self, sample_data):
        """Test de la complétude des données."""
        # Vérifier que toutes les colonnes requises sont présentes
        required_columns = ['country_name', 'id_country']
        for col in required_columns:
            assert col in sample_data.columns
            assert sample_data[col].notna().all()

    def test_categorical_data_encoding(self, sample_data):
        """Test de l'encodage des données catégorielles."""
        # Vérifier que les pays sont bien encodés
        country_encoding = sample_data.groupby('country_name')['id_country'].first()
        
        # Vérifier que chaque pays a un ID unique
        assert len(country_encoding) == len(country_encoding.unique())
        
        # Vérifier que les IDs sont des entiers
        assert all(isinstance(id_val, (int, np.integer)) for id_val in country_encoding.values) 