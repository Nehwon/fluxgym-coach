"""Script de benchmark pour tester les performances du cache d'images."""

import argparse
import os
import shutil
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fluxgym_coach.cli import main as fluxgym_main
from fluxgym_coach.image_cache import ImageCache


def prepare_test_environment(num_images: int, base_dir: Path) -> Path:
    """Prépare un environnement de test avec des images factices.
    
    Args:
        num_images: Nombre d'images à créer
        base_dir: Répertoire de base pour les tests
        
    Returns:
        Chemin vers le dossier d'entrée créé
    """
    input_dir = base_dir / "input"
    input_dir.mkdir(exist_ok=True, parents=True)
    
    # Créer des images factices
    for i in range(num_images):
        (input_dir / f"image_{i:04d}.jpg").write_text(f"Fichier image de test {i}")
    
    return input_dir


def run_benchmark(input_dir: Path, output_dir: Path, use_cache: bool = True, force_reprocess: bool = False) -> float:
    """Exécute un benchmark avec ou sans cache.
    
    Args:
        input_dir: Dossier d'entrée contenant les images
        output_dir: Dossier de sortie pour les résultats
        use_cache: Si True, utilise le cache
        force_reprocess: Si True, force le retraitement même si en cache
        
    Returns:
        Temps d'exécution en secondes
    """
    # Nettoyer le dossier de sortie
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # Construire les arguments de ligne de commande
    args = [
        "--input", str(input_dir),
        "--output", str(output_dir),
        "--process", "all"
    ]
    
    if not use_cache:
        args.append("--no-cache")
    
    if force_reprocess:
        args.append("--force-reprocess")
    
    # Désactiver la sortie verbeuse pour le benchmark
    if "--verbose" in args:
        args.remove("--verbose")
    
    # Exécuter et mesurer le temps
    start_time = time.time()
    result = fluxgym_main(args)
    end_time = time.time()
    
    if result != 0:
        print(f"Erreur lors de l'exécution avec {'cache' if use_cache else 'sans cache'}")
        return float('inf')
    
    return end_time - start_time


def main():
    """Fonction principale du benchmark."""
    parser = argparse.ArgumentParser(description="Benchmark du cache d'images Fluxgym-coach")
    parser.add_argument(
        "-n", "--num-images", type=int, default=10,
        help="Nombre d'images à utiliser pour le test (défaut: 10)"
    )
    parser.add_argument(
        "-r", "--runs", type=int, default=3,
        help="Nombre d'exécutions pour chaque configuration (défaut: 3)"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Nettoyer les dossiers de test après l'exécution"
    )
    
    args = parser.parse_args()
    
    # Préparer les dossiers de test
    base_dir = Path("benchmark_results")
    base_dir.mkdir(exist_ok=True)
    
    input_dir = prepare_test_environment(args.num_images, base_dir)
    
    print(f"Benchmark avec {args.num_images} images et {args.runs} exécutions par configuration")
    print("=" * 50)
    
    # Exécuter les benchmarks
    results = {
        "Avec cache (première exécution)": [],
        "Avec cache (exécutions suivantes)": [],
        "Sans cache": []
    }
    
    # Première exécution avec cache (mise en cache)
    print("\nPremière exécution avec cache (mise en cache)...")
    for i in range(args.runs):
        output_dir = base_dir / f"output_with_cache_first_{i}"
        duration = run_benchmark(input_dir, output_dir, use_cache=True, force_reprocess=True)
        results["Avec cache (première exécution)"].append(duration)
        print(f"  Exécution {i+1}/{args.runs}: {duration:.2f} secondes")
    
    # Exécutions suivantes avec cache (utilisation du cache)
    print("\nExécutions suivantes avec cache (utilisation du cache)...")
    for i in range(args.runs):
        output_dir = base_dir / f"output_with_cache_next_{i}"
        duration = run_benchmark(input_dir, output_dir, use_cache=True, force_reprocess=False)
        results["Avec cache (exécutions suivantes)"].append(duration)
        print(f"  Exécution {i+1}/{args.runs}: {duration:.2f} secondes")
    
    # Exécutions sans cache
    print("\nExécutions sans cache...")
    for i in range(args.runs):
        output_dir = base_dir / f"output_without_cache_{i}"
        duration = run_benchmark(input_dir, output_dir, use_cache=False)
        results["Sans cache"].append(duration)
        print(f"  Exécution {i+1}/{args.runs}: {duration:.2f} secondes")
    
    # Afficher les résultats
    print("\nRésultats du benchmark:")
    print("=" * 50)
    print(f"{'Configuration':<40} | {'Moyenne':>10} | {'Min':>10} | {'Max':>10} | Écart-type")
    print("-" * 80)
    
    for config, times in results.items():
        if not times:
            continue
            
        avg = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = (sum((t - avg) ** 2 for t in times) / len(times)) ** 0.5
        
        print(f"{config:<40} | {avg:>10.2f}s | {min_time:>8.2f}s | {max_time:>8.2f}s | ±{std_dev:.2f}s")
    
    # Nettoyer si demandé
    if args.clean:
        print("\nNettoyage des fichiers de test...")
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    main()
