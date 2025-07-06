"""
Test rapide pour vérifier l'installation des tests

Ce module contient des tests simples pour vérifier que l'environnement de test
est correctement configuré.
"""

import pytest
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test que tous les imports nécessaires fonctionnent."""
    try:
        import pandas as pd
        import numpy as np
        from prophet import Prophet
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        import psycopg2
        import joblib
        import matplotlib.pyplot as plt
        
        # Test des imports locaux
        from db.connection import get_connection
        import common.utils as utils
        
        assert True, "Tous les imports fonctionnent"
    except ImportError as e:
        pytest.fail(f"Import échoué: {e}")


def test_fixtures(sample_data, temp_directories, mock_connection):
    """Test que les fixtures de base fonctionnent."""
    # Test des données d'exemple
    assert sample_data is not None
    assert len(sample_data) > 0
    assert 'country_name' in sample_data.columns
    
    # Test des répertoires temporaires
    assert temp_directories is not None
    assert 'models_dir' in temp_directories
    assert 'predictions_dir' in temp_directories
    assert 'plots_dir' in temp_directories
    
    # Test de la connexion mockée
    mock_conn, mock_cursor = mock_connection
    assert mock_conn is not None
    assert mock_cursor is not None


def test_prophet_basic():
    """Test basique de Prophet."""
    try:
        from prophet import Prophet
        import pandas as pd
        import numpy as np
        
        # Créer des données de test simples
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'ds': dates,
            'y': [100 + i * 2 for i in range(10)]
        })
        
        # Créer et entraîner un modèle simple
        model = Prophet()
        model.fit(data)
        
        # Faire une prédiction simple
        future = model.make_future_dataframe(periods=5)
        forecast = model.predict(future)
        
        assert 'yhat' in forecast.columns
        assert len(forecast) == len(data) + 5
        
    except Exception as e:
        pytest.fail(f"Test Prophet échoué: {e}")


def test_sklearn_metrics():
    """Test des métriques sklearn."""
    try:
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        import numpy as np
        
        # Données de test
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 1.9, 3.1, 3.9, 5.1])
        
        # Calculer les métriques
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # Vérifications
        assert rmse > 0
        assert mae > 0
        assert r2 > 0
        
    except Exception as e:
        pytest.fail(f"Test sklearn échoué: {e}")


def test_file_operations(temp_directories):
    """Test des opérations de fichiers."""
    try:
        import pandas as pd
        import joblib
        import matplotlib.pyplot as plt
        
        # Test de création de CSV
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        csv_path = os.path.join(temp_directories['predictions_dir'], 'test.csv')
        df.to_csv(csv_path, index=False)
        assert os.path.exists(csv_path)
        
        # Test de sauvegarde de modèle
        model = {'test': 'model'}
        model_path = os.path.join(temp_directories['models_dir'], 'test.pkl')
        joblib.dump(model, model_path)
        assert os.path.exists(model_path)
        
        # Test de création de graphique
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
        plot_path = os.path.join(temp_directories['plots_dir'], 'test.png')
        fig.savefig(plot_path)
        plt.close(fig)
        assert os.path.exists(plot_path)
        
    except Exception as e:
        pytest.fail(f"Test fichiers échoué: {e}")


def test_database_mock(mock_connection):
    """Test des mocks de base de données."""
    try:
        mock_conn, mock_cursor = mock_connection
        
        # Simuler une requête
        mock_cursor.execute("SELECT 1")
        mock_cursor.fetchone.return_value = (1,)
        result = mock_cursor.fetchone()
        
        assert result == (1,)
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        
    except Exception as e:
        pytest.fail(f"Test base de données échoué: {e}")


def test_environment():
    """Test de l'environnement de test."""
    # Vérifier que nous sommes dans le bon répertoire
    assert os.path.exists("main.py"), "main.py doit exister"
    assert os.path.exists("tests/"), "Répertoire tests doit exister"
    
    # Vérifier les modules locaux
    assert os.path.exists("db/connection.py"), "db/connection.py doit exister"
    assert os.path.exists("common/utils.py"), "common/utils.py doit exister"


if __name__ == "__main__":
    # Exécution directe pour test rapide
    print("🧪 Test rapide de l'environnement de test...")
    
    try:
        test_imports()
        print("✅ Imports OK")
        
        # Créer des fixtures temporaires pour le test
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_directories = {
                'models_dir': os.path.join(temp_dir, 'models'),
                'predictions_dir': os.path.join(temp_dir, 'predictions'),
                'plots_dir': os.path.join(temp_dir, 'plots')
            }
            os.makedirs(temp_directories['models_dir'])
            os.makedirs(temp_directories['predictions_dir'])
            os.makedirs(temp_directories['plots_dir'])
            
            test_file_operations(temp_directories)
            print("✅ Opérations de fichiers OK")
        
        test_prophet_basic()
        print("✅ Prophet OK")
        
        test_sklearn_metrics()
        print("✅ Sklearn OK")
        
        test_environment()
        print("✅ Environnement OK")
        
        print("\n🎉 Tous les tests rapides sont passés!")
        print("L'environnement de test est correctement configuré.")
        
    except Exception as e:
        print(f"\n❌ Test échoué: {e}")
        print("Vérifiez l'installation des dépendances.")
        sys.exit(1) 