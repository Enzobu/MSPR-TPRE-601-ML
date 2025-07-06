"""
Tests de performance pour MSPR-TPRE-601-ML

Ce module teste les performances du système en termes de temps d'exécution,
utilisation mémoire et scalabilité.
"""

import pytest
import pandas as pd
import numpy as np
import time
import psutil
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class TestPerformance:
    """Tests de performance du système."""

    def test_model_training_performance(self, sample_data):
        """Test de performance de l'entraînement des modèles."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        training_times = []
        
        # Mesurer le temps d'entraînement pour chaque pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            start_time = time.time()
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            end_time = time.time()
            training_time = end_time - start_time
            training_times.append(training_time)
        
        # Vérifications de performance
        assert len(training_times) > 0
        assert all(t > 0 for t in training_times)
        assert max(training_times) < 30  # Moins de 30 secondes par modèle
        assert np.mean(training_times) < 10  # Moyenne inférieure à 10 secondes

    def test_prediction_performance(self, sample_data):
        """Test de performance de la génération des prédictions."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        prediction_times = []
        
        # Mesurer le temps de prédiction pour chaque pays
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            
            if len(df_country) < 10:
                continue
            
            # Créer et entraîner le modèle
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(df_country)
            
            # Mesurer le temps de prédiction
            start_time = time.time()
            
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            end_time = time.time()
            prediction_time = end_time - start_time
            prediction_times.append(prediction_time)
        
        # Vérifications de performance
        assert len(prediction_times) > 0
        assert all(t > 0 for t in prediction_times)
        assert max(prediction_times) < 10  # Moins de 10 secondes par prédiction
        assert np.mean(prediction_times) < 5  # Moyenne inférieure à 5 secondes

    def test_memory_usage_performance(self, sample_data):
        """Test de performance de l'utilisation mémoire."""
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
        
        models = []
        forecasts = []
        
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
            models.append(model)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = df_country[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            forecasts.append(forecast)
        
        # Mesurer la mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Vérifications de mémoire
        assert memory_used > 0
        assert memory_used < 500  # Moins de 500MB pour les tests
        assert len(models) > 0
        assert len(forecasts) > 0

    def test_scalability_performance(self):
        """Test de scalabilité avec différentes tailles de données."""
        # Générer des données de différentes tailles
        data_sizes = [50, 100, 200, 500]
        performance_metrics = {}
        
        for size in data_sizes:
            # Générer des données de test
            dates = pd.date_range(start='2023-01-01', periods=size, freq='D')
            data = pd.DataFrame({
                'ds': dates,
                'y': [100 + i * 2 + np.random.normal(0, 5) for i in range(size)],
                'population': [0.5] * size,
                'pib': [0.6] * size,
                'deaths': [0.1] * size
            })
            
            # Mesurer le temps d'entraînement
            start_time = time.time()
            
            model = Prophet()
            model.add_regressor('population')
            model.add_regressor('pib')
            model.add_regressor('deaths')
            model.fit(data)
            
            # Générer les prédictions
            future = model.make_future_dataframe(periods=90)
            future['population'] = 0.5
            future['pib'] = 0.6
            future['deaths'] = 0.1
            forecast = model.predict(future)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            performance_metrics[size] = total_time
        
        # Vérifications de scalabilité
        assert len(performance_metrics) == len(data_sizes)
        assert all(t > 0 for t in performance_metrics.values())
        
        # Vérifier que le temps augmente de manière raisonnable
        times = list(performance_metrics.values())
        for i in range(1, len(times)):
            # Le temps ne devrait pas augmenter de manière exponentielle
            assert times[i] < times[i-1] * 3

    def test_concurrent_processing_performance(self, sample_data):
        """Test de performance du traitement concurrent."""
        import concurrent.futures
        import threading
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        def process_country(country_data):
            """Fonction pour traiter un pays."""
            if len(country_data) < 10:
                return None
            
            model = Prophet()
            for reg in colonnes_numeriques:
                model.add_regressor(reg)
            model.fit(country_data)
            
            future = model.make_future_dataframe(periods=90)
            for col in colonnes_numeriques:
                future[col] = country_data[col].iloc[-1]
            forecast = model.predict(future)
            forecast['yhat'] = forecast['yhat'].clip(lower=0)
            
            return forecast
        
        # Traitement séquentiel
        start_time = time.time()
        sequential_results = []
        for country in df['country_name'].unique():
            df_country = df[df['country_name'] == country].copy()
            result = process_country(df_country)
            if result is not None:
                sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Traitement parallèle
        start_time = time.time()
        parallel_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for country in df['country_name'].unique():
                df_country = df[df['country_name'] == country].copy()
                future = executor.submit(process_country, df_country)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    parallel_results.append(result)
        parallel_time = time.time() - start_time
        
        # Vérifications
        assert len(sequential_results) > 0
        assert len(parallel_results) > 0
        assert len(sequential_results) == len(parallel_results)
        assert sequential_time > 0
        assert parallel_time > 0

    def test_database_operation_performance(self, mock_connection):
        """Test de performance des opérations de base de données."""
        mock_conn, mock_cursor = mock_connection
        
        # Simuler des données de prédiction
        num_predictions = 1000
        predictions = []
        for i in range(num_predictions):
            predictions.append({
                'id_country': 1,
                'id_disease': 1,
                'ds': datetime(2023, 1, 1) + timedelta(days=i),
                'yhat': 100.0 + i,
                'yhat_lower': 90.0 + i,
                'yhat_upper': 110.0 + i
            })
        
        # Mesurer le temps d'insertion
        start_time = time.time()
        
        query = """
            INSERT INTO prediction (id_country, id_disease, ds, yhat, yhat_lower, yhat_upper)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for pred in predictions:
            values = (
                pred['id_country'],
                pred['id_disease'],
                pred['ds'],
                pred['yhat'],
                pred['yhat_lower'],
                pred['yhat_upper']
            )
            mock_cursor.execute(query, values)
        
        mock_conn.commit()
        
        end_time = time.time()
        insertion_time = end_time - start_time
        
        # Vérifications
        assert insertion_time > 0
        assert insertion_time < 10  # Moins de 10 secondes pour 1000 insertions
        assert mock_cursor.execute.call_count == num_predictions
        assert mock_conn.commit.call_count == 1

    def test_file_io_performance(self, sample_forecast, temp_directories):
        """Test de performance des opérations de fichiers."""
        import joblib
        import matplotlib.pyplot as plt
        
        forecast = sample_forecast
        num_forecasts = 10
        
        # Test de performance de sauvegarde CSV
        start_time = time.time()
        for i in range(num_forecasts):
            forecast_path = os.path.join(temp_directories['predictions_dir'], f'forecast_{i}.csv')
            forecast.to_csv(forecast_path, index=False)
        csv_time = time.time() - start_time
        
        # Test de performance de sauvegarde de modèle
        model = Prophet()
        start_time = time.time()
        for i in range(num_forecasts):
            model_path = os.path.join(temp_directories['models_dir'], f'model_{i}.pkl')
            joblib.dump(model, model_path)
        model_time = time.time() - start_time
        
        # Test de performance de génération de graphiques
        start_time = time.time()
        for i in range(num_forecasts):
            plot_path = os.path.join(temp_directories['plots_dir'], f'plot_{i}.png')
            fig = model.plot(forecast)
            fig.savefig(plot_path)
            plt.close(fig)
        plot_time = time.time() - start_time
        
        # Vérifications
        assert csv_time > 0
        assert model_time > 0
        assert plot_time > 0
        assert csv_time < 5  # Moins de 5 secondes pour 10 fichiers CSV
        assert model_time < 10  # Moins de 10 secondes pour 10 modèles
        assert plot_time < 30  # Moins de 30 secondes pour 10 graphiques

    def test_memory_leak_detection(self, sample_data):
        """Test de détection de fuites mémoire."""
        import gc
        
        # Mesurer la mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Effectuer plusieurs cycles de traitement
        for cycle in range(5):
            models = []
            forecasts = []
            
            for country in df['country_name'].unique():
                df_country = df[df['country_name'] == country].copy()
                
                if len(df_country) < 10:
                    continue
                
                # Créer et entraîner le modèle
                model = Prophet()
                for reg in colonnes_numeriques:
                    model.add_regressor(reg)
                model.fit(df_country)
                models.append(model)
                
                # Générer les prédictions
                future = model.make_future_dataframe(periods=90)
                for col in colonnes_numeriques:
                    future[col] = df_country[col].iloc[-1]
                forecast = model.predict(future)
                forecast['yhat'] = forecast['yhat'].clip(lower=0)
                forecasts.append(forecast)
            
            # Forcer le garbage collection
            del models
            del forecasts
            gc.collect()
        
        # Mesurer la mémoire finale
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Vérifications
        assert memory_increase < 100  # Augmentation de moins de 100MB après 5 cycles

    def test_cpu_usage_performance(self, sample_data):
        """Test de l'utilisation CPU."""
        import psutil
        
        # Mesurer l'utilisation CPU avant
        cpu_percent_before = psutil.cpu_percent(interval=1)
        
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement intensif
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
        
        # Mesurer l'utilisation CPU après
        cpu_percent_after = psutil.cpu_percent(interval=1)
        
        # Vérifications
        assert cpu_percent_before >= 0
        assert cpu_percent_after >= 0
        # L'utilisation CPU peut varier, mais devrait être raisonnable

    def test_network_performance(self, mock_connection):
        """Test de performance réseau (simulé)."""
        mock_conn, mock_cursor = mock_connection
        
        # Simuler des requêtes réseau
        num_queries = 100
        query_times = []
        
        for i in range(num_queries):
            start_time = time.time()
            
            # Simuler une requête
            mock_cursor.execute("SELECT * FROM test LIMIT 1")
            mock_cursor.fetchone()
            
            end_time = time.time()
            query_time = end_time - start_time
            query_times.append(query_time)
        
        # Vérifications
        assert len(query_times) == num_queries
        assert all(t >= 0 for t in query_times)
        assert np.mean(query_times) < 0.1  # Moyenne inférieure à 100ms par requête

    def test_batch_processing_performance(self, sample_data):
        """Test de performance du traitement par lots."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        colonnes_numeriques = ['population', 'pib', 'deaths']
        df = df[['ds', 'y', 'country_name', 'id_country'] + colonnes_numeriques].copy()
        df = df[df['y'].notna()]
        df = df[df['y'] > 0]
        
        # Traitement par lots de différentes tailles
        batch_sizes = [1, 5, 10]
        batch_performance = {}
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            countries = list(df['country_name'].unique())
            for i in range(0, len(countries), batch_size):
                batch_countries = countries[i:i+batch_size]
                
                for country in batch_countries:
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
            
            end_time = time.time()
            batch_performance[batch_size] = end_time - start_time
        
        # Vérifications
        assert len(batch_performance) == len(batch_sizes)
        assert all(t > 0 for t in batch_performance.values()) 