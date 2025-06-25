"""Script de benchmark pour tester les performances du cache d'images."""

import argparse
import os
import shutil
import sys
import time
import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Ajouter le répertoire parent au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fluxgym_coach.cli import main as fluxgym_main
from fluxgym_coach.image_cache import ImageCache


def create_test_image(
    width: int = 800, height: int = 600, text: str = ""
) -> Image.Image:
    """Crée une image de test avec un dégradé et du texte.

    Args:
        width: Largeur de l'image
        height: Hauteur de l'image
        text: Texte à afficher sur l'image

    Returns:
        Image PIL générée
    """
    # Créer une image avec un dégradé
    arr = np.zeros((height, width, 3), dtype=np.uint8)

    # Ajouter un dégradé de couleur aléatoire
    r1, g1, b1 = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    r2, g2, b2 = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    for y in range(height):
        r = int(r1 + (r2 - r1) * y / height)
        g = int(g1 + (g2 - g1) * y / height)
        b = int(b1 + (b2 - b1) * y / height)
        arr[y, :] = [r, g, b]

    img = Image.fromarray(arr)

    # Ajouter du texte si fourni
    if text:
        try:
            draw = ImageDraw.Draw(img)
            # Essayer d'utiliser une police par défaut
            try:
                font = ImageFont.truetype("Arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default()

            # Positionner le texte au centre
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2

            # Ajouter un contour noir pour une meilleure lisibilité
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill="black")

            # Ajouter le texte principal en blanc
            draw.text((x, y), text, font=font, fill="white")
        except Exception as e:
            print(f"Avertissement: Impossible d'ajouter du texte à l'image: {e}")

    return img


def prepare_test_environment(num_images: int, base_dir: Path) -> Path:
    """Prépare un environnement de test avec des images factices.

    Args:
        num_images: Nombre d'images à créer
        base_dir: Répertoire de base pour les tests

    Returns:
        Chemin vers le dossier d'entrée créé
    """
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"

    # Nettoyer les dossiers existants
    for d in [input_dir, output_dir]:
        if d.exists():
            shutil.rmtree(d)

    # Créer les dossiers
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    print(f"Création de {num_images} images de test dans {input_dir}...")

    # Créer des images factices
    for i in range(num_images):
        img = create_test_image(
            width=random.randint(400, 1200),
            height=random.randint(300, 900),
            text=f"Test Image {i:03d}",
        )
        img_path = input_dir / f"image_{i:04d}.jpg"
        img.save(img_path, "JPEG", quality=90)
        print(f"  Créé: {img_path}")

    return input_dir


def run_benchmark(
    input_dir: Path,
    output_dir: Path,
    use_cache: bool = True,
    force_reprocess: bool = False,
) -> float:
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
    args = ["--input", str(input_dir), "--output", str(output_dir), "--process", "all"]

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
        print(
            f"Erreur lors de l'exécution avec {'cache' if use_cache else 'sans cache'}"
        )
        return float("inf")

    return end_time - start_time


def main():
    """Fonction principale du benchmark."""
    parser = argparse.ArgumentParser(
        description="Benchmark du cache d'images Fluxgym-coach"
    )
    parser.add_argument(
        "-n",
        "--num-images",
        type=int,
        default=5,
        help="Nombre d'images à utiliser pour le test (défaut: 5)",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=3,
        help="Nombre d'exécutions pour chaque configuration (défaut: 3)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Nettoyer les dossiers de test après l'exécution",
    )

    args = parser.parse_args()

    # Préparer les dossiers de test
    base_dir = Path("benchmark_results")
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    input_dir = prepare_test_environment(args.num_images, base_dir)

    print(
        f"Benchmark avec {args.num_images} images et {args.runs} exécutions par configuration"
    )
    print("=" * 50)

    # Exécuter les benchmarks
    results = {
        "Avec cache (première exécution)": [],
        "Avec cache (exécutions suivantes)": [],
        "Sans cache": [],
    }

    # Première exécution avec cache (mise en cache)
    print("\nPremière exécution avec cache (mise en cache)...")
    for i in range(args.runs):
        output_dir = base_dir / f"output_with_cache_first_{i}"
        duration = run_benchmark(
            input_dir, output_dir, use_cache=True, force_reprocess=True
        )
        results["Avec cache (première exécution)"].append(duration)
        print(f"  Exécution {i+1}/{args.runs}: {duration:.2f} secondes")

    # Exécutions suivantes avec cache (utilisation du cache)
    print("\nExécutions suivantes avec cache (utilisation du cache)...")
    for i in range(args.runs):
        output_dir = base_dir / f"output_with_cache_next_{i}"
        duration = run_benchmark(
            input_dir, output_dir, use_cache=True, force_reprocess=False
        )
        results["Avec cache (exécutions suivantes)"].append(duration)
        print(f"  Exécution {i+1}/{args.runs}: {duration:.2f} secondes")

    # Exécutions sans cache
    print("\nExécutions sans cache...")
    for i in range(args.runs):
        output_dir = base_dir / f"output_without_cache_{i}"
        duration = run_benchmark(input_dir, output_dir, use_cache=False)
        results["Sans cache"].append(duration)
        print(f"  Exécution {i+1}/{args.runs}: {duration:.2f} secondes")

    # Afficher les résultats de manière plus lisible
    print("\n" + "=" * 80)
    print("RÉSULTATS DU BENCHMARK".center(80))
    print("=" * 80)

    # Calculer les statistiques
    stats = {}
    for config, times in results.items():
        if not times:
            continue

        times = [t for t in times if t < float("inf")]  # Filtrer les échecs
        if not times:
            continue

        avg = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = (sum((t - avg) ** 2 for t in times) / len(times)) ** 0.5

        stats[config] = {"avg": avg, "min": min_time, "max": max_time, "std": std_dev}

    # Afficher le tableau des résultats
    print("\n" + "-" * 80)
    print(
        f"{'CONFIGURATION':<40} | {'MOYENNE':>10} | {'MIN':>8} | {'MAX':>8} | ÉCART-TYPE"
    )
    print("-" * 80)

    for config, data in stats.items():
        print(
            f"{config:<40} | {data['avg']:>8.2f}s | {data['min']:>6.2f}s | {data['max']:>6.2f}s | ±{data['std']:.2f}s"
        )

    # Afficher le gain de performance
    if len(stats) >= 2:
        first = next(iter(stats.values()))
        last = list(stats.values())[-1]
        if first["avg"] > 0 and last["avg"] > 0:
            gain = (first["avg"] - last["avg"]) / first["avg"] * 100
            print("\n" + "-" * 80)
            print(
                f"GAIN DE PERFORMANCE: {abs(gain):.1f}% {'d''amélioration' if gain > 0 else 'de perte'}"
            )
            print("-" * 80)

    # Nettoyer si demandé
    if args.clean:
        print("\nNettoyage des fichiers de test...")
        shutil.rmtree(base_dir)


if __name__ == "__main__":
    main()
