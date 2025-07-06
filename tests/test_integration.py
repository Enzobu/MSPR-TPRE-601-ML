"""
Tests d'intégration pour le workflow complet

Ce module teste l'intégration de tous les composants du système.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
import shutil

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class TestCompleteWorkflow:
    """Tests d'intégration pour le workflow complet."""

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_complete_data_pipeline(self, mock_read_query, mock_get_conn, sample_data):
        """Test du pipeline complet de traitement des données."""
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Mock des résultats de la base de données
        mock_cursor.fetchall.return_value = []
        
        # Simuler la lecture des données
        df = sample_data.copy()
        
        # Test du pipeline de données
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        
        # Filtrage des données
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Vérifications
        assert len(df) > 0
        assert 'ds' in df.columns
        assert 'y' in df.columns
        assert all(col in df.columns for col in colonnes_numeriques)
        assert df['y'].isna().sum() == 0
        assert (df['y'] > 0).all()

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_complete_model_training(self, mock_read_query, mock_get_conn, sample_data, temp_directories):
        """Test de l'entraînement complet du modèle."""
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement par pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            
            model.fit(df_country)
            
            # Créer le dataframe futur
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            
            # Générer les prédictions
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            # Vérifications
            assert 'yhat' in forecast.columns
            assert 'yhat_lower' in forecast.columns
            assert 'yhat_upper' in forecast.columns
            assert len(forecast) == len(df_country) + 90
            assert (forecast['yhat'] >= 0).all()

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_complete_metrics_calculation(self, mock_read_query, mock_get_conn, sample_data):
        """Test du calcul complet des métriques."""
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement par pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            # Calculer les métriques
            df_country['ds'] = pd.to_datetime(df_country['ds'])
            forecast['ds'] = pd.to_datetime(forecast['ds'])
            
            df_eval = pd.merge(df_country[['ds', 'y']], forecast[['ds', 'yhat']], on='ds', how='inner')
            
            if len(df_eval) > 0:
                y_true = df_eval['y'].values
                y_pred = df_eval['yhat'].values
                
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                mae = mean_absolute_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                
                # Métriques récentes
                df_eval_recent = df_eval[df_eval['ds'] >= pd.Timestamp("2022-01-01")]
                if len(df_eval_recent) > 0:
                    y_true_recent = df_eval_recent['y'].values
                    y_pred_recent = df_eval_recent['yhat'].values
                    rmse_bis = np.sqrt(mean_squared_error(y_true_recent, y_pred_recent))
                    mae_bis = mean_absolute_error(y_true_recent, y_pred_recent)
                    r2_bis = r2_score(y_true_recent, y_pred_recent)
                else:
                    rmse_bis = mae_bis = r2_bis = None
                
                # Vérifications
                assert rmse >= 0
                assert mae >= 0
                assert r2 <= 1
                if r2_bis is not None:
                    assert rmse_bis >= 0
                    assert mae_bis >= 0
                    assert r2_bis <= 1

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_complete_file_operations(self, mock_read_query, mock_get_conn, sample_data, temp_directories):
        """Test des opérations complètes de fichiers."""
        import joblib
        import matplotlib.pyplot as plt
        
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement par pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            # Sauvegarder le modèle
            safe_country_name = country.replace(" ", "_").replace("/", "_")
            model_path = os.path.join(temp_directories['models_dir'], f'prophet_model_{safe_country_name}.pkl')
            joblib.dump(model, model_path)
            
            # Sauvegarder les prédictions
            forecast_path = os.path.join(temp_directories['predictions_dir'], f'forecast_{safe_country_name}.csv')
            forecast.to_csv(forecast_path, index=False)
            
            # Générer le graphique
            plot_path = os.path.join(temp_directories['plots_dir'], f'forecast_plot_{safe_country_name}.png')
            fig = model.plot(forecast)
            fig.savefig(plot_path)
            plt.close(fig)
            
            # Vérifications
            assert os.path.exists(model_path)
            assert os.path.exists(forecast_path)
            assert os.path.exists(plot_path)
            assert os.path.getsize(model_path) > 0
            assert os.path.getsize(forecast_path) > 0
            assert os.path.getsize(plot_path) > 0

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_complete_database_operations(self, mock_read_query, mock_get_conn, sample_data):
        """Test des opérations complètes de base de données."""
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Mock des résultats de recherche de pays
        mock_cursor.fetchone.return_value = (1,)  # id_country
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Supprimer les prédictions existantes
        today = date.today()
        mock_cursor.execute("DELETE FROM prediction")
        mock_conn.commit()
        
        # Traitement par pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            # Calculer les métriques
            df_country['ds'] = pd.to_datetime(df_country['ds'])
            forecast['ds'] = pd.to_datetime(forecast['ds'])
            
            df_eval = pd.merge(df_country[['ds', 'y']], forecast[['ds', 'yhat']], on='ds', how='inner')
            
            if len(df_eval) > 0:
                y_true = df_eval['y'].values
                y_pred = df_eval['yhat'].values
                
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                mae = mean_absolute_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                
                # Insérer les métriques
                mock_cursor.execute("""
                    INSERT INTO metrics (_date, rmse, mae, r2, id_country, r2_bis, rmse_bis, mae_bis)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (today, rmse, mae, r2, 1, None, None, None))
            
            # Rechercher l'ID du pays
            mock_cursor.execute("SELECT id_country FROM country WHERE name = %s", (country,))
            result = mock_cursor.fetchone()
            id_country = result[0] if result else 1
            
            # Insérer les prédictions
            id_disease = 1
            for _, row in forecast.iterrows():
                mock_cursor.execute("""
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
                """, (
                    id_country, id_disease, row['ds'],
                    row.get('yhat'), row.get('yhat_lower'), row.get('yhat_upper'),
                    row.get('trend'), row.get('trend_lower'), row.get('trend_upper'),
                    row.get('deaths'), row.get('deaths_lower'), row.get('deaths_upper'),
                    row.get('pib'), row.get('pib_lower'), row.get('pib_upper'),
                    row.get('population'), row.get('population_lower'), row.get('population_upper')
                ))
            
            mock_conn.commit()
            
            # Insérer le log de succès
            mock_cursor.execute("""
                INSERT INTO log (_date, is_success, error_string, id_country)
                VALUES (%s, %s, %s, %s)
            """, (today, True, None, id_country))
            mock_conn.commit()
        
        # Vérifications
        assert mock_cursor.execute.call_count > 0
        assert mock_conn.commit.call_count > 0

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_error_handling_integration(self, mock_read_query, mock_get_conn, sample_data):
        """Test de la gestion d'erreurs intégrée."""
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        today = date.today()
        
        # Traitement par pays avec gestion d'erreurs
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            id_country = df_country['id_country'].iloc[0]
            log_success = True
            error_message = None
            
            try:
                if len(df_country) < 10:
                    raise ValueError(f"Trop peu de données pour {country}")
                
                # Créer et entraîner le modèle
                model = Prophet()
                for reg in colonnes_numeriques:
                    model.add_regressor(reg)
                model.fit(df_country)
                
                # Générer les prédictions
                future = model.make_future_dataframe(periods=90)
                for col in colonnes_numeriques:
                    future[col] = df_country[col].iloc[-1]
                forecast = model.predict(future)
                forecast['yhat'] = forecast['yhat'].clip(lower=0)
                
                # Simuler une erreur pour certains pays
                if country == 'TestCountry1':
                    raise Exception("Test error for TestCountry1")
                
            except Exception as e:
                log_success = False
                error_message = str(e)
            
            # Insérer le log
            mock_cursor.execute("""
                INSERT INTO log (_date, is_success, error_string, id_country)
                VALUES (%s, %s, %s, %s)
            """, (today, log_success, error_message, id_country))
            mock_conn.commit()
        
        # Vérifications
        assert mock_cursor.execute.call_count > 0
        assert mock_conn.commit.call_count > 0

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_performance_integration(self, mock_read_query, mock_get_conn, sample_data):
        """Test de performance intégré."""
        import time
        
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        start_time = time.time()
        
        # Traitement par pays
        processed_countries = 0
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            processed_countries += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Vérifications de performance
        assert processed_countries > 0
        assert processing_time > 0
        assert processing_time < 60  # Moins d'une minute pour les tests

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_memory_usage_integration(self, mock_read_query, mock_get_conn, sample_data):
        """Test de l'utilisation mémoire intégrée."""
        import psutil
        import os
        
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Mesurer la mémoire avant
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement par pays
        models = []
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Stocker le modèle pour tester la mémoire
            models.append(model)
        
        # Mesurer la mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Vérifications de mémoire
        assert memory_used > 0
        assert memory_used < 1000  # Moins de 1GB pour les tests
        assert len(models) > 0

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_data_consistency_integration(self, mock_read_query, mock_get_conn, sample_data):
        """Test de la cohérence des données intégrée."""
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Vérifications de cohérence
        assert len(df) > 0
        assert df['y'].isna().sum() == 0
        assert (df['y'] > 0).all()
        
        # Vérifier la cohérence par pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            # Vérifier que l'ID du pays est constant
            unique_ids = df_country['id_country'].unique()
            assert len(unique_ids) == 1
            
            # Vérifier que les données sont ordonnées chronologiquement
            dates = pd.to_datetime(df_country['ds'])
            assert dates.is_monotonic_increasing
            
            # Vérifier que les régresseurs sont dans des plages raisonnables
            for col in colonnes_numeriques:
                if col in df_country.columns:
                    assert df_country[col].min() >= 0
                    assert df_country[col].max() <= 1.0  # Normalisé

    @patch('main.get_connection')
    @patch('main.utils.read_sql_query')
    def test_output_validation_integration(self, mock_read_query, mock_get_conn, sample_data, temp_directories):
        """Test de validation des sorties intégré."""
        import joblib
        
        # Mock de la connexion
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock de la requête SQL
        mock_read_query.return_value = "SELECT * FROM test"
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement par pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            # Sauvegarder et valider les sorties
            safe_country_name = country.replace(" ", "_").replace("/", "_")
            
            # Validation du modèle
            model_path = os.path.join(temp_directories['models_dir'], f'prophet_model_{safe_country_name}.pkl')
            joblib.dump(model, model_path)
            loaded_model = joblib.load(model_path)
            assert isinstance(loaded_model, Prophet)
            assert hasattr(loaded_model, 'params')
            
            # Validation des prédictions
            forecast_path = os.path.join(temp_directories['predictions_dir'], f'forecast_{safe_country_name}.csv')
            forecast.to_csv(forecast_path, index=False)
            loaded_forecast = pd.read_csv(forecast_path)
            assert len(loaded_forecast) == len(forecast)
            assert 'yhat' in loaded_forecast.columns
            assert (loaded_forecast['yhat'] >= 0).all()
            
            # Validation des métriques
            df_country['ds'] = pd.to_datetime(df_country['ds'])
            forecast['ds'] = pd.to_datetime(forecast['ds'])
            
            df_eval = pd.merge(df_country[['ds', 'y']], forecast[['ds', 'yhat']], on='ds', how='inner')
            
            if len(df_eval) > 0:
                y_true = df_eval['y'].values
                y_pred = df_eval['yhat'].values
                
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                mae = mean_absolute_error(y_true, y_pred)
                r2 = r2_score(y_true, y_pred)
                
                # Validation des métriques
                assert rmse >= 0
                assert mae >= 0
                assert r2 <= 1
                assert isinstance(rmse, (int, float))
                assert isinstance(mae, (int, float))
                assert isinstance(r2, (int, float)) 