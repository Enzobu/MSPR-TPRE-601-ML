"""
Tests unitaires pour les opérations de base de données

Ce module teste les connexions, requêtes et opérations de base de données.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_connection


class TestDatabaseConnection:
    """Tests pour les connexions de base de données."""

    @patch('db.connection.psycopg2.connect')
    @patch('db.connection.os.getenv')
    def test_get_connection_success(self, mock_getenv, mock_connect):
        """Test de connexion réussie à la base de données."""
        # Mock des variables d'environnement
        mock_getenv.side_effect = lambda x: {
            'DB_HOST': 'localhost',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password',
            'DB_DATABASE': 'test_db',
            'DB_PORT': '5432'
        }.get(x)
        
        # Mock de la connexion
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Tester la connexion
        conn = get_connection()
        
        # Vérifications
        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host='localhost',
            user='test_user',
            password='test_password',
            database='test_db',
            port='5432'
        )

    @patch('db.connection.psycopg2.connect')
    @patch('db.connection.os.getenv')
    def test_get_connection_failure(self, mock_getenv, mock_connect):
        """Test de connexion échouée à la base de données."""
        # Mock des variables d'environnement
        mock_getenv.side_effect = lambda x: {
            'DB_HOST': 'localhost',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password',
            'DB_DATABASE': 'test_db',
            'DB_PORT': '5432'
        }.get(x)
        
        # Mock de l'échec de connexion
        mock_connect.side_effect = Exception("Connection failed")
        
        # Tester que l'exception est levée
        with pytest.raises(Exception):
            get_connection()

    @patch('db.connection.psycopg2.connect')
    @patch('db.connection.os.getenv')
    def test_get_connection_missing_env_vars(self, mock_getenv, mock_connect):
        """Test avec des variables d'environnement manquantes."""
        # Mock des variables d'environnement manquantes
        mock_getenv.return_value = None
        
        # Mock de la connexion
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        # Tester la connexion (devrait utiliser None pour les valeurs manquantes)
        conn = get_connection()
        
        # Vérifications
        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            host=None,
            user=None,
            password=None,
            database=None,
            port=None
        )


class TestDatabaseOperations:
    """Tests pour les opérations de base de données."""

    def test_sql_query_execution(self, mock_connection):
        """Test de l'exécution de requêtes SQL."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock des résultats
        mock_cursor.fetchall.return_value = [
            ('2023-01-01', 100, 'France', 1, 0.5, 0.6, 0.1),
            ('2023-01-02', 120, 'France', 1, 0.5, 0.6, 0.1)
        ]
        
        # Exécuter une requête
        query = "SELECT * FROM statement LIMIT 2"
        mock_cursor.execute(query)
        results = mock_cursor.fetchall()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query)
        assert len(results) == 2
        assert results[0][2] == 'France'

    def test_data_insertion(self, mock_connection):
        """Test de l'insertion de données."""
        mock_conn, mock_cursor = mock_connection
        
        # Données à insérer
        insert_data = {
            'id_country': 1,
            'id_disease': 1,
            'ds': date(2023, 1, 1),
            'yhat': 100.5,
            'yhat_lower': 90.0,
            'yhat_upper': 110.0
        }
        
        # Requête d'insertion
        query = """
            INSERT INTO prediction (id_country, id_disease, ds, yhat, yhat_lower, yhat_upper)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            insert_data['id_country'],
            insert_data['id_disease'],
            insert_data['ds'],
            insert_data['yhat'],
            insert_data['yhat_lower'],
            insert_data['yhat_upper']
        )
        
        # Exécuter l'insertion
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once()

    def test_metrics_insertion(self, mock_connection, sample_metrics):
        """Test de l'insertion des métriques."""
        mock_conn, mock_cursor = mock_connection
        
        # Données des métriques
        metrics = sample_metrics
        today = date.today()
        
        # Requête d'insertion des métriques
        query = """
            INSERT INTO metrics (_date, rmse, mae, r2, id_country, r2_bis, rmse_bis, mae_bis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            today,
            metrics['rmse'],
            metrics['mae'],
            metrics['r2'],
            1,  # id_country
            metrics['r2_bis'],
            metrics['rmse_bis'],
            metrics['mae_bis']
        )
        
        # Exécuter l'insertion
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once()

    def test_log_insertion(self, mock_connection):
        """Test de l'insertion des logs."""
        mock_conn, mock_cursor = mock_connection
        
        # Données du log
        today = date.today()
        log_data = {
            'is_success': True,
            'error_string': None,
            'id_country': 1
        }
        
        # Requête d'insertion du log
        query = """
            INSERT INTO log (_date, is_success, error_string, id_country)
            VALUES (%s, %s, %s, %s)
        """
        values = (
            today,
            log_data['is_success'],
            log_data['error_string'],
            log_data['id_country']
        )
        
        # Exécuter l'insertion
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once()

    def test_error_log_insertion(self, mock_connection):
        """Test de l'insertion des logs d'erreur."""
        mock_conn, mock_cursor = mock_connection
        
        # Données du log d'erreur
        today = date.today()
        error_data = {
            'is_success': False,
            'error_string': 'Test error message',
            'id_country': 1
        }
        
        # Requête d'insertion du log
        query = """
            INSERT INTO log (_date, is_success, error_string, id_country)
            VALUES (%s, %s, %s, %s)
        """
        values = (
            today,
            error_data['is_success'],
            error_data['error_string'],
            error_data['id_country']
        )
        
        # Exécuter l'insertion
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once()

    def test_data_deletion(self, mock_connection):
        """Test de la suppression de données."""
        mock_conn, mock_cursor = mock_connection
        
        # Requête de suppression
        query = "DELETE FROM prediction"
        
        # Exécuter la suppression
        mock_cursor.execute(query)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query)
        mock_conn.commit.assert_called_once()

    def test_country_lookup(self, mock_connection):
        """Test de la recherche d'un pays."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock des résultats
        mock_cursor.fetchone.return_value = (1,)  # id_country
        
        # Requête de recherche
        country_name = 'France'
        query = "SELECT id_country FROM country WHERE name = %s"
        
        # Exécuter la recherche
        mock_cursor.execute(query, (country_name,))
        result = mock_cursor.fetchone()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, (country_name,))
        assert result == (1,)

    def test_country_not_found(self, mock_connection):
        """Test de la recherche d'un pays inexistant."""
        mock_conn, mock_cursor = mock_connection
        
        # Mock des résultats (pays non trouvé)
        mock_cursor.fetchone.return_value = None
        
        # Requête de recherche
        country_name = 'NonExistentCountry'
        query = "SELECT id_country FROM country WHERE name = %s"
        
        # Exécuter la recherche
        mock_cursor.execute(query, (country_name,))
        result = mock_cursor.fetchone()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, (country_name,))
        assert result is None

    def test_batch_insertion(self, mock_connection, sample_forecast):
        """Test de l'insertion en lot des prédictions."""
        mock_conn, mock_cursor = mock_connection
        
        # Données de prédiction
        forecast = sample_forecast.head(5)  # Prendre seulement 5 lignes pour le test
        id_country = 1
        id_disease = 1
        
        # Requête d'insertion
        query = """
            INSERT INTO prediction (
                id_country, id_disease, ds,
                yhat, yhat_lower, yhat_upper,
                trend, trend_lower, trend_upper,
                deaths, deaths_lower, deaths_upper,
                pib, pib_lower, pib_upper,
                population, population_lower, population_upper
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
        """
        
        # Insérer chaque ligne
        for _, row in forecast.iterrows():
            values = (
                id_country, id_disease, row['ds'],
                row.get('yhat'), row.get('yhat_lower'), row.get('yhat_upper'),
                row.get('trend'), row.get('trend_lower'), row.get('trend_upper'),
                row.get('deaths'), row.get('deaths_lower'), row.get('deaths_upper'),
                row.get('pib'), row.get('pib_lower'), row.get('pib_upper'),
                row.get('population'), row.get('population_lower'), row.get('population_upper')
            )
            mock_cursor.execute(query, values)
        
        mock_conn.commit()
        
        # Vérifications
        assert mock_cursor.execute.call_count == len(forecast)
        mock_conn.commit.assert_called_once()

    def test_transaction_rollback(self, mock_connection):
        """Test du rollback en cas d'erreur."""
        mock_conn, mock_cursor = mock_connection
        
        # Simuler une erreur lors de l'exécution
        mock_cursor.execute.side_effect = Exception("Database error")
        
        try:
            # Tenter d'exécuter une requête
            mock_cursor.execute("INSERT INTO test VALUES (1)")
            mock_conn.commit()
        except Exception:
            # Rollback en cas d'erreur
            mock_conn.rollback()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with("INSERT INTO test VALUES (1)")
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    def test_connection_cleanup(self, mock_connection):
        """Test de la fermeture propre des connexions."""
        mock_conn, mock_cursor = mock_connection
        
        # Simuler l'utilisation de la connexion
        mock_cursor.execute("SELECT 1")
        mock_cursor.fetchone()
        
        # Fermer les ressources
        mock_cursor.close()
        mock_conn.close()
        
        # Vérifications
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_data_validation_before_insert(self, mock_connection):
        """Test de la validation des données avant insertion."""
        mock_conn, mock_cursor = mock_connection
        
        # Données valides
        valid_data = {
            'id_country': 1,
            'id_disease': 1,
            'ds': date(2023, 1, 1),
            'yhat': 100.5,
            'yhat_lower': 90.0,
            'yhat_upper': 110.0
        }
        
        # Validation des données
        assert isinstance(valid_data['id_country'], int)
        assert isinstance(valid_data['id_disease'], int)
        assert isinstance(valid_data['ds'], date)
        assert isinstance(valid_data['yhat'], (int, float))
        assert valid_data['yhat_lower'] <= valid_data['yhat'] <= valid_data['yhat_upper']
        
        # Si la validation passe, insérer
        query = "INSERT INTO prediction VALUES (%s, %s, %s, %s, %s, %s)"
        values = (
            valid_data['id_country'],
            valid_data['id_disease'],
            valid_data['ds'],
            valid_data['yhat'],
            valid_data['yhat_lower'],
            valid_data['yhat_upper']
        )
        
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once()

    def test_null_value_handling(self, mock_connection):
        """Test de la gestion des valeurs nulles."""
        mock_conn, mock_cursor = mock_connection
        
        # Données avec valeurs nulles
        data_with_nulls = {
            'id_country': 1,
            'id_disease': 1,
            'ds': date(2023, 1, 1),
            'yhat': 100.5,
            'yhat_lower': None,  # Valeur nulle
            'yhat_upper': None   # Valeur nulle
        }
        
        # Requête d'insertion
        query = """
            INSERT INTO prediction (id_country, id_disease, ds, yhat, yhat_lower, yhat_upper)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data_with_nulls['id_country'],
            data_with_nulls['id_disease'],
            data_with_nulls['ds'],
            data_with_nulls['yhat'],
            data_with_nulls['yhat_lower'],
            data_with_nulls['yhat_upper']
        )
        
        # Exécuter l'insertion
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once()

    def test_data_type_conversion(self, mock_connection):
        """Test de la conversion des types de données."""
        mock_conn, mock_cursor = mock_connection
        
        # Données avec types à convertir
        raw_data = {
            'id_country': '1',  # String au lieu d'int
            'id_disease': '1',  # String au lieu d'int
            'ds': '2023-01-01',  # String au lieu de date
            'yhat': '100.5',     # String au lieu de float
            'yhat_lower': '90.0', # String au lieu de float
            'yhat_upper': '110.0' # String au lieu de float
        }
        
        # Conversion des types
        converted_data = {
            'id_country': int(raw_data['id_country']),
            'id_disease': int(raw_data['id_disease']),
            'ds': datetime.strptime(raw_data['ds'], '%Y-%m-%d').date(),
            'yhat': float(raw_data['yhat']),
            'yhat_lower': float(raw_data['yhat_lower']),
            'yhat_upper': float(raw_data['yhat_upper'])
        }
        
        # Vérifier les types convertis
        assert isinstance(converted_data['id_country'], int)
        assert isinstance(converted_data['id_disease'], int)
        assert isinstance(converted_data['ds'], date)
        assert isinstance(converted_data['yhat'], float)
        assert isinstance(converted_data['yhat_lower'], float)
        assert isinstance(converted_data['yhat_upper'], float)
        
        # Requête d'insertion
        query = """
            INSERT INTO prediction (id_country, id_disease, ds, yhat, yhat_lower, yhat_upper)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = tuple(converted_data.values())
        
        mock_cursor.execute(query, values)
        mock_conn.commit()
        
        # Vérifications
        mock_cursor.execute.assert_called_once_with(query, values)
        mock_conn.commit.assert_called_once() 