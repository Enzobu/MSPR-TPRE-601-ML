#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests MSPR-TPRE-601-ML

Ce script permet d'exécuter différents types de tests avec des options configurables.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_command(command, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Commande: {command}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Durée: {duration:.2f} secondes")
        print(f"Code de retour: {result.returncode}")
        
        if result.stdout:
            print("\n📤 Sortie standard:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  Erreurs:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ {description} - SUCCÈS")
        else:
            print(f"\n❌ {description} - ÉCHEC")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n💥 Erreur lors de l'exécution: {e}")
        return False


def run_unit_tests(verbose=False, coverage=False):
    """Exécute les tests unitaires."""
    command = "python -m pytest tests/ -v" if verbose else "python -m pytest tests/"
    
    if coverage:
        command = "python -m pytest tests/ --cov=. --cov-report=html --cov-report=term"
    
    return run_command(command, "Tests unitaires")


def run_integration_tests(verbose=False):
    """Exécute les tests d'intégration."""
    command = "python -m pytest tests/test_integration.py -v" if verbose else "python -m pytest tests/test_integration.py"
    return run_command(command, "Tests d'intégration")


def run_performance_tests(verbose=False):
    """Exécute les tests de performance."""
    command = "python -m pytest tests/test_performance.py -v" if verbose else "python -m pytest tests/test_performance.py"
    return run_command(command, "Tests de performance")


def run_data_processing_tests(verbose=False):
    """Exécute les tests de traitement des données."""
    command = "python -m pytest tests/test_data_processing.py -v" if verbose else "python -m pytest tests/test_data_processing.py"
    return run_command(command, "Tests de traitement des données")


def run_prophet_model_tests(verbose=False):
    """Exécute les tests du modèle Prophet."""
    command = "python -m pytest tests/test_prophet_model.py -v" if verbose else "python -m pytest tests/test_prophet_model.py"
    return run_command(command, "Tests du modèle Prophet")


def run_database_tests(verbose=False):
    """Exécute les tests de base de données."""
    command = "python -m pytest tests/test_database_operations.py -v" if verbose else "python -m pytest tests/test_database_operations.py"
    return run_command(command, "Tests de base de données")


def run_linting():
    """Exécute le linting du code."""
    command = "python -m pylint main.py db/ common/ --disable=C0114,C0115,C0116"
    return run_command(command, "Linting du code")


def run_type_checking():
    """Exécute la vérification des types."""
    command = "python -m mypy main.py db/ common/ --ignore-missing-imports"
    return run_command(command, "Vérification des types")


def run_security_scan():
    """Exécute un scan de sécurité basique."""
    command = "python -m bandit -r . -f json -o security_report.json"
    return run_command(command, "Scan de sécurité")


def generate_test_report():
    """Génère un rapport de tests."""
    command = "python -m pytest tests/ --html=test_report.html --self-contained-html"
    return run_command(command, "Génération du rapport de tests")


def install_test_dependencies():
    """Installe les dépendances de test."""
    dependencies = [
        "pytest",
        "pytest-cov",
        "pytest-html",
        "pylint",
        "mypy",
        "bandit",
        "psutil"
    ]
    
    for dep in dependencies:
        command = f"pip install {dep}"
        success = run_command(command, f"Installation de {dep}")
        if not success:
            print(f"⚠️  Échec de l'installation de {dep}")
            return False
    
    return True


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Script d'exécution des tests MSPR-TPRE-601-ML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python tests/run_tests.py --all                    # Tous les tests
  python tests/run_tests.py --unit --verbose         # Tests unitaires avec sortie détaillée
  python tests/run_tests.py --integration            # Tests d'intégration uniquement
  python tests/run_tests.py --performance            # Tests de performance uniquement
  python tests/run_tests.py --coverage               # Tests avec couverture de code
  python tests/run_tests.py --install-deps           # Installer les dépendances
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Exécuter tous les tests et vérifications"
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Exécuter les tests unitaires"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Exécuter les tests d'intégration"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Exécuter les tests de performance"
    )
    
    parser.add_argument(
        "--data-processing",
        action="store_true",
        help="Exécuter les tests de traitement des données"
    )
    
    parser.add_argument(
        "--prophet",
        action="store_true",
        help="Exécuter les tests du modèle Prophet"
    )
    
    parser.add_argument(
        "--database",
        action="store_true",
        help="Exécuter les tests de base de données"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Afficher la sortie détaillée"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Générer un rapport de couverture de code"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Exécuter le linting du code"
    )
    
    parser.add_argument(
        "--type-check",
        action="store_true",
        help="Vérifier les types"
    )
    
    parser.add_argument(
        "--security",
        action="store_true",
        help="Exécuter le scan de sécurité"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Générer un rapport de tests HTML"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Installer les dépendances de test"
    )
    
    args = parser.parse_args()
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("main.py"):
        print("❌ Erreur: Ce script doit être exécuté depuis le répertoire racine du projet")
        sys.exit(1)
    
    print("🧪 Tests MSPR-TPRE-601-ML")
    print("=" * 50)
    
    # Installer les dépendances si demandé
    if args.install_deps:
        if not install_test_dependencies():
            print("❌ Échec de l'installation des dépendances")
            sys.exit(1)
        print("✅ Dépendances installées avec succès")
        return
    
    # Si aucun argument spécifique n'est fourni, afficher l'aide
    if not any([
        args.all, args.unit, args.integration, args.performance,
        args.data_processing, args.prophet, args.database,
        args.lint, args.type_check, args.security, args.report
    ]):
        parser.print_help()
        return
    
    # Exécuter les tests selon les arguments
    results = []
    
    if args.all:
        print("🎯 Exécution de tous les tests et vérifications...")
        results.extend([
            ("Linting", run_linting()),
            ("Vérification des types", run_type_checking()),
            ("Scan de sécurité", run_security_scan()),
            ("Tests unitaires", run_unit_tests(args.verbose, args.coverage)),
            ("Tests d'intégration", run_integration_tests(args.verbose)),
            ("Tests de performance", run_performance_tests(args.verbose)),
            ("Rapport de tests", generate_test_report())
        ])
    else:
        if args.lint:
            results.append(("Linting", run_linting()))
        
        if args.type_check:
            results.append(("Vérification des types", run_type_checking()))
        
        if args.security:
            results.append(("Scan de sécurité", run_security_scan()))
        
        if args.unit:
            results.append(("Tests unitaires", run_unit_tests(args.verbose, args.coverage)))
        
        if args.integration:
            results.append(("Tests d'intégration", run_integration_tests(args.verbose)))
        
        if args.performance:
            results.append(("Tests de performance", run_performance_tests(args.verbose)))
        
        if args.data_processing:
            results.append(("Tests de traitement des données", run_data_processing_tests(args.verbose)))
        
        if args.prophet:
            results.append(("Tests du modèle Prophet", run_prophet_model_tests(args.verbose)))
        
        if args.database:
            results.append(("Tests de base de données", run_database_tests(args.verbose)))
        
        if args.report:
            results.append(("Rapport de tests", generate_test_report()))
    
    # Afficher le résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {len(results)} tests")
    print(f"Passés: {passed}")
    print(f"Échoués: {failed}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} test(s) ont échoué")
        sys.exit(1)
    else:
        print(f"\n🎉 Tous les tests sont passés avec succès!")


if __name__ == "__main__":
    main() 