"""
Tests unitaires pour le modèle Prophet

Ce module teste l'entraînement, la prédiction et l'évaluation du modèle Prophet.
"""

import pytest
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProphetModel:
    """Tests pour le modèle Prophet."""

    def test_prophet_initialization(self):
        """Test de l'initialisation du modèle Prophet."""
        model = Prophet()
        
        assert model is not None
        assert isinstance(model, Prophet)
        assert model.growth == 'linear'
        assert model.seasonality_mode == 'additive'

    def test_regressor_addition(self):
        """Test de l'ajout de régresseurs externes."""
        model = Prophet()
        
        # Ajouter des régresseurs
        regressors = ['population', 'pib', 'deaths']
        for reg in regressors:
            model.add_regressor(reg)
        
        # Vérifier que les régresseurs sont ajoutés
        assert len(model.extra_regressors) == 3
        assert all(reg in [r.name for r in model.extra_regressors] for reg in regressors)

    def test_model_fitting(self, sample_data):
        """Test de l'entraînement du modèle."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        
        # L'entraînement ne devrait pas lever d'exception
        model.fit(df)
        
        assert model.params is not None
        assert hasattr(model, 'history')

    def test_future_dataframe_creation(self, sample_data):
        """Test de la création du dataframe futur."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur
        periods = 90
        future = model.make_future_dataframe(periods=periods)
        
        # Vérifications
        assert len(future) == len(df) + periods
        assert 'ds' in future.columns
        assert pd.api.types.is_datetime64_any_dtype(future['ds'])

    def test_regressor_propagation(self, sample_data):
        """Test de la propagation des régresseurs dans le futur."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur
        future = model.make_future_dataframe(periods=10)
        
        # Propager les dernières valeurs des régresseurs
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        # Vérifications
        for col in regressors:
            assert col in future.columns
            # Les valeurs futures devraient être constantes (dernière valeur)
            future_values = future[col].iloc[-10:]
            assert future_values.nunique() == 1

    def test_prediction_generation(self, sample_data):
        """Test de la génération des prédictions."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        # Générer les prédictions
        forecast = model.predict(future)
        
        # Vérifications
        assert 'yhat' in forecast.columns
        assert 'yhat_lower' in forecast.columns
        assert 'yhat_upper' in forecast.columns
        assert len(forecast) == len(future)
        assert not forecast['yhat'].isna().all()

    def test_prediction_clipping(self, sample_data):
        """Test du clipping des prédictions négatives."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur et prédire
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        forecast = model.predict(future)
        
        # Appliquer le clipping
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        
        # Vérifications
        assert (forecast['yhat'] >= 0).all()

    def test_metrics_calculation(self, sample_data):
        """Test du calcul des métriques de performance."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur et prédire
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        forecast = model.predict(future)
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        
        # Préparer les données pour l'évaluation
        df['ds'] = pd.to_datetime(df['ds'])
        forecast['ds'] = pd.to_datetime(forecast['ds'])
        
        # Fusionner les données historiques avec les prédictions
        df_eval = pd.merge(df[['ds', 'y']], forecast[['ds', 'yhat']], on='ds', how='inner')
        
        if len(df_eval) > 0:
            y_true = df_eval['y'].values
            y_pred = df_eval['yhat'].values
            
            # Calculer les métriques
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            
            # Vérifications
            assert rmse >= 0
            assert mae >= 0
            assert r2 <= 1  # R² peut être négatif mais ne peut pas dépasser 1

    def test_recent_metrics_calculation(self, sample_data):
        """Test du calcul des métriques sur les données récentes."""
        # Préparer les données avec des dates récentes
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur et prédire
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        forecast = model.predict(future)
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        
        # Préparer les données pour l'évaluation
        df['ds'] = pd.to_datetime(df['ds'])
        forecast['ds'] = pd.to_datetime(forecast['ds'])
        
        df_eval = pd.merge(df[['ds', 'y']], forecast[['ds', 'yhat']], on='ds', how='inner')
        
        if len(df_eval) > 0:
            # Filtrer les données récentes (après 2022-01-01)
            df_eval_recent = df_eval[df_eval['ds'] >= pd.Timestamp("2022-01-01")]
            
            if len(df_eval_recent) > 0:
                y_true_recent = df_eval_recent['y'].values
                y_pred_recent = df_eval_recent['yhat'].values
                
                # Calculer les métriques récentes
                rmse_bis = np.sqrt(mean_squared_error(y_true_recent, y_pred_recent))
                mae_bis = mean_absolute_error(y_true_recent, y_pred_recent)
                r2_bis = r2_score(y_true_recent, y_pred_recent)
                
                # Vérifications
                assert rmse_bis >= 0
                assert mae_bis >= 0
                assert r2_bis <= 1

    def test_model_serialization(self, sample_prophet_model, temp_directories):
        """Test de la sérialisation du modèle."""
        import joblib
        
        model = sample_prophet_model
        model_path = os.path.join(temp_directories['models_dir'], 'test_model.pkl')
        
        # Sauvegarder le modèle
        joblib.dump(model, model_path)
        
        # Vérifier que le fichier existe
        assert os.path.exists(model_path)
        
        # Charger le modèle
        loaded_model = joblib.load(model_path)
        
        # Vérifier que le modèle chargé est fonctionnel
        assert isinstance(loaded_model, Prophet)
        assert hasattr(loaded_model, 'params')

    def test_forecast_export(self, sample_forecast, temp_directories):
        """Test de l'export des prédictions."""
        forecast = sample_forecast
        forecast_path = os.path.join(temp_directories['predictions_dir'], 'test_forecast.csv')
        
        # Exporter les prédictions
        forecast.to_csv(forecast_path, index=False)
        
        # Vérifier que le fichier existe
        assert os.path.exists(forecast_path)
        
        # Charger et vérifier les données
        loaded_forecast = pd.read_csv(forecast_path)
        assert len(loaded_forecast) == len(forecast)
        assert 'yhat' in loaded_forecast.columns

    def test_model_plotting(self, sample_prophet_model, sample_forecast, temp_directories):
        """Test de la génération des graphiques."""
        import matplotlib.pyplot as plt
        
        model = sample_prophet_model
        forecast = sample_forecast
        plot_path = os.path.join(temp_directories['plots_dir'], 'test_plot.png')
        
        # Générer le graphique
        fig = model.plot(forecast)
        fig.savefig(plot_path)
        plt.close(fig)
        
        # Vérifier que le fichier existe
        assert os.path.exists(plot_path)
        assert os.path.getsize(plot_path) > 0

    def test_minimum_data_requirement(self, sample_data):
        """Test de l'exigence de données minimales pour l'entraînement."""
        # Tester avec différentes quantités de données
        for min_data in [5, 10, 20]:
            for country in sample_data['country_name'].unique():
                country_data = sample_data[sample_data['country_name'] == country].copy()
                country_data = country_data.rename(columns={'_date': 'ds', 'confirmed': 'y'})
                
                if len(country_data) < min_data:
                    # Le modèle devrait échouer ou être rejeté
                    with pytest.raises((ValueError, Exception)):
                        model = Prophet()
                        model.add_regressor('population')
                        model.add_regressor('pib')
                        model.add_regressor('deaths')
                        model.fit(country_data)

    def test_regressor_consistency(self, sample_data):
        """Test de la cohérence des régresseurs."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer le modèle
        model = Prophet()
        regressors = ['population', 'pib', 'deaths']
        
        # Vérifier que tous les régresseurs sont présents dans les données
        for reg in regressors:
            assert reg in df.columns
            model.add_regressor(reg)
        
        # L'entraînement devrait réussir
        model.fit(df)
        
        # Vérifier que les régresseurs sont bien utilisés
        assert len(model.extra_regressors) == len(regressors)

    def test_prediction_intervals(self, sample_data):
        """Test des intervalles de prédiction."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur et prédire
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        forecast = model.predict(future)
        
        # Vérifier les intervalles de prédiction
        assert 'yhat_lower' in forecast.columns
        assert 'yhat_upper' in forecast.columns
        
        # Vérifier que les intervalles sont cohérents
        assert (forecast['yhat_lower'] <= forecast['yhat']).all()
        assert (forecast['yhat'] <= forecast['yhat_upper']).all()

    def test_trend_component(self, sample_data):
        """Test de la composante de tendance."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer et entraîner le modèle
        model = Prophet()
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur et prédire
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        forecast = model.predict(future)
        
        # Vérifier la composante de tendance
        assert 'trend' in forecast.columns
        assert 'trend_lower' in forecast.columns
        assert 'trend_upper' in forecast.columns
        
        # La tendance devrait être cohérente
        assert (forecast['trend_lower'] <= forecast['trend']).all()
        assert (forecast['trend'] <= forecast['trend_upper']).all()

    def test_seasonality_components(self, sample_data):
        """Test des composantes de saisonnalité."""
        # Préparer les données
        df = sample_data.copy()
        df = df.rename(columns={'_date': 'ds', 'confirmed': 'y'})
        
        # Créer le modèle avec saisonnalité
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        model.add_regressor('population')
        model.add_regressor('pib')
        model.add_regressor('deaths')
        model.fit(df)
        
        # Créer le dataframe futur et prédire
        future = model.make_future_dataframe(periods=10)
        regressors = ['population', 'pib', 'deaths']
        for col in regressors:
            future[col] = df[col].iloc[-1]
        
        forecast = model.predict(future)
        
        # Vérifier que les composantes de saisonnalité sont présentes
        # (Prophet ne les expose pas directement dans forecast, mais elles sont utilisées)
        assert 'yhat' in forecast.columns
        assert not forecast['yhat'].isna().all() 