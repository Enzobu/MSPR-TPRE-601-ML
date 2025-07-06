#!/usr/bin/env python3
"""
Script d'installation des dépendances de test pour MSPR-TPRE-601-ML

Ce script installe les dépendances minimales nécessaires pour exécuter les tests.
"""

import subprocess
import sys
import os


def install_package(package):
    """Installe un package avec pip."""
    try:
        print(f"📦 Installation de {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec de l'installation de {package}: {e}")
        if e.stderr:
            print(f"Erreur: {e.stderr}")
        return False


def check_package(package):
    """Vérifie si un package est installé."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def main():
    """Fonction principale."""
    print("🔧 Installation des dépendances de test MSPR-TPRE-601-ML")
    print("=" * 60)
    
    # Dépendances minimales pour les tests
    dependencies = [
        "pytest",
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "psutil"
    ]
    
    # Dépendances optionnelles (peuvent échouer sans problème)
    optional_dependencies = [
        "prophet",
        "psycopg2-binary",
        "joblib"
    ]
    
    print("📋 Dépendances minimales:")
    for dep in dependencies:
        if check_package(dep.replace("-", "_")):
            print(f"✅ {dep} (déjà installé)")
        else:
            if not install_package(dep):
                print(f"❌ Impossible d'installer {dep}")
                return False
    
    print("\n📋 Dépendances optionnelles:")
    for dep in optional_dependencies:
        if check_package(dep.replace("-", "_")):
            print(f"✅ {dep} (déjà installé)")
        else:
            print(f"⚠️  Tentative d'installation de {dep}...")
            if install_package(dep):
                print(f"✅ {dep} installé")
            else:
                print(f"⚠️  {dep} non installé (optionnel)")
    
    print("\n" + "=" * 60)
    print("🎯 Vérification de l'installation...")
    
    # Vérifier les imports essentiels
    essential_imports = [
        ("pytest", "pytest"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("psutil", "psutil")
    ]
    
    failed_imports = []
    for package_name, import_name in essential_imports:
        if check_package(import_name):
            print(f"✅ {package_name}")
        else:
            print(f"❌ {package_name}")
            failed_imports.append(package_name)
    
    if failed_imports:
        print(f"\n❌ Échec de l'installation: {', '.join(failed_imports)}")
        return False
    
    print("\n🎉 Installation réussie!")
    print("Vous pouvez maintenant exécuter les tests avec:")
    print("  python3 tests/test_quick.py")
    print("  python3 tests/run_tests.py --unit")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 