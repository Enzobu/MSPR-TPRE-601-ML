"""
Configuration pytest pour les tests MSPR-TPRE-601-ML

Ce fichier contient les fixtures communes utilisées par tous les tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from unittest.mock import Mock, patch
import psycopg2
from prophet import Prophet


@pytest.fixture
def sample_data():
    """
    Fixture fournissant des données d'exemple pour les tests.
    
    Returns:
        pd.DataFrame: Données de test avec structure similaire aux données réelles
    """
    # Générer des dates sur 100 jours
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Données pour 3 pays fictifs
    countries = ['TestCountry1', 'TestCountry2', 'TestCountry3']
    
    data = []
    for country in countries:
        country_id = hash(country) % 1000  # ID simple basé sur le hash
        
        for i, date in enumerate(dates):
            # Générer des données réalistes avec tendance et bruit
            base_value = 100 + i * 2  # Tendance croissante
            noise = np.random.normal(0, 10)  # Bruit gaussien
            confirmed = max(0, int(base_value + noise))
            
            # Données socio-économiques normalisées
            population = np.random.uniform(0.1, 1.0)
            pib = np.random.uniform(0.1, 1.0)
            deaths = np.random.uniform(0.0, 0.5)
            
            data.append({
                'ds': date,
                'y': confirmed,
                'country_name': country,
                'id_country': country_id,
                'population': population,
                'pib': pib,
                'deaths': deaths
            })
    
    return pd.DataFrame(data)


@pytest.fixture
def mock_connection():
    """
    Fixture fournissant une connexion de base de données mockée.
    
    Returns:
        Mock: Objet mock simulant une connexion PostgreSQL
    """
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def temp_directories():
    """
    Fixture créant des répertoires temporaires pour les tests.
    
    Yields:
        dict: Dictionnaire avec les chemins des répertoires temporaires
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        models_dir = os.path.join(temp_dir, 'models')
        predictions_dir = os.path.join(temp_dir, 'predictions')
        plots_dir = os.path.join(temp_dir, 'plots')
        
        os.makedirs(models_dir, exist_ok=True)
        os.makedirs(predictions_dir, exist_ok=True)
        os.makedirs(plots_dir, exist_ok=True)
        
        yield {
            'temp_dir': temp_dir,
            'models_dir': models_dir,
            'predictions_dir': predictions_dir,
            'plots_dir': plots_dir
        }


@pytest.fixture
def sample_prophet_model():
    """
    Fixture fournissant un modèle Prophet entraîné pour les tests.
    
    Returns:
        Prophet: Modèle Prophet entraîné avec des données de test
    """
    # Créer des données de test
    dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
    data = pd.DataFrame({
        'ds': dates,
        'y': [100 + i * 2 + np.random.normal(0, 5) for i in range(50)],
        'population': [0.5] * 50,
        'pib': [0.6] * 50,
        'deaths': [0.1] * 50
    })
    
    # Créer et entraîner le modèle
    model = Prophet()
    model.add_regressor('population')
    model.add_regressor('pib')
    model.add_regressor('deaths')
    model.fit(data)
    
    return model


@pytest.fixture
def sample_forecast():
    """
    Fixture fournissant des prédictions Prophet pour les tests.
    
    Returns:
        pd.DataFrame: DataFrame avec les prédictions Prophet
    """
    # Créer des données de base
    dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
    data = pd.DataFrame({
        'ds': dates,
        'y': [100 + i * 2 + np.random.normal(0, 5) for i in range(50)],
        'population': [0.5] * 50,
        'pib': [0.6] * 50,
        'deaths': [0.1] * 50
    })
    
    # Créer le modèle et faire des prédictions
    model = Prophet()
    model.add_regressor('population')
    model.add_regressor('pib')
    model.add_regressor('deaths')
    model.fit(data)
    
    future = model.make_future_dataframe(periods=10)
    future['population'] = 0.5
    future['pib'] = 0.6
    future['deaths'] = 0.1
    
    forecast = model.predict(future)
    return forecast


@pytest.fixture
def mock_environment_variables():
    """
    Fixture mockant les variables d'environnement de base de données.
    
    Returns:
        dict: Variables d'environnement mockées
    """
    return {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_DATABASE': 'test_database',
        'DB_PORT': '5432'
    }


@pytest.fixture
def sample_metrics():
    """
    Fixture fournissant des métriques d'exemple pour les tests.
    
    Returns:
        dict: Métriques de performance simulées
    """
    return {
        'rmse': 15.5,
        'mae': 12.3,
        'r2': 0.85,
        'rmse_bis': 14.2,
        'mae_bis': 11.8,
        'r2_bis': 0.87
    }


@pytest.fixture
def mock_sql_query():
    """
    Fixture fournissant une requête SQL mockée.
    
    Returns:
        str: Requête SQL de test
    """
    return """
    SELECT 
        s._date AS ds,
        s.confirmed AS y,
        c.population,
        c.pib,
        s.deaths,
        c.name as country_name,
        c.id_country
    FROM statement s
    JOIN country c ON s.id_country = c.id_country
    WHERE s.id_disease = 1
    ORDER BY c.name, s._date;
    """


@pytest.fixture(scope="session")
def test_database_schema():
    """
    Fixture définissant le schéma de base de données pour les tests.
    
    Returns:
        list: Liste des commandes SQL pour créer les tables de test
    """
    return [
        """
        CREATE TABLE IF NOT EXISTS country (
            id_country SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            population DECIMAL(15,4),
            pib DECIMAL(15,4),
            continent VARCHAR(50)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS disease (
            id_disease SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS statement (
            id_statement SERIAL PRIMARY KEY,
            id_country INTEGER REFERENCES country(id_country),
            id_disease INTEGER REFERENCES disease(id_disease),
            _date DATE NOT NULL,
            confirmed INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            recovered INTEGER DEFAULT 0
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS prediction (
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
        """,
        """
        CREATE TABLE IF NOT EXISTS metrics (
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
        """,
        """
        CREATE TABLE IF NOT EXISTS log (
            id_log SERIAL PRIMARY KEY,
            _date DATE NOT NULL,
            is_success BOOLEAN NOT NULL,
            error_string TEXT,
            id_country INTEGER REFERENCES country(id_country)
        );
        """
    ]


@pytest.fixture
def expected_columns():
    """
    Fixture définissant les colonnes attendues dans les DataFrames.
    
    Returns:
        list: Liste des noms de colonnes attendus
    """
    return ['ds', 'y', 'country_name', 'id_country', 'population', 'pib', 'deaths']


@pytest.fixture
def test_countries():
    """
    Fixture fournissant une liste de pays de test.
    
    Returns:
        list: Liste des noms de pays pour les tests
    """
    return ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom']


@pytest.fixture
def mock_file_paths():
    """
    Fixture fournissant des chemins de fichiers mockés.
    
    Returns:
        dict: Dictionnaire avec les chemins de fichiers
    """
    return {
        'query_sql': './query/query.sql',
        'model_path': 'models/prophet_model_TestCountry.pkl',
        'prediction_path': 'predictions/forecast_TestCountry.csv',
        'plot_path': 'plots/forecast_plot_TestCountry.png'
    } 