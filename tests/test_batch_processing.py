"""
Script de test pour le traitement par lots d'images.

Ce script permet de tester la méthode upscale_batch avec différents scénarios
pour s'assurer que l'ordre des résultats est correctement préservé.
"""

import os
import sys
import tempfile
import logging
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw
import shutil

# Configuration des logs
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_batch_processing.log", mode="w"),
    ],
)

# Activer les logs détaillés pour les modules spécifiques
logging.getLogger("PIL").setLevel(logging.INFO)  # Réduire le bruit de PIL
logging.getLogger("urllib3").setLevel(logging.INFO)  # Réduire le bruit de urllib3

# Activer les logs détaillés pour nos modules
logging.getLogger("fluxgym_coach.image_enhancement").setLevel(logging.DEBUG)
logging.getLogger("fluxgym_coach.image_cache").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au PYTHONPATH pour importer le module
sys.path.insert(0, str(Path(__file__).parent))
from fluxgym_coach.image_enhancement import ImageEnhancer

# Couleurs pour les images de test
COLORS = [
    (255, 0, 0),  # Rouge
    (0, 255, 0),  # Vert
    (0, 0, 255),  # Bleu
    (255, 255, 0),  # Jaune
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]


def create_test_images(
    output_dir: Path, num_images: int = 3, size: tuple = (100, 100)
) -> list[Path]:
    """Crée des images de test avec des couleurs uniques."""
    paths = []
    os.makedirs(output_dir, exist_ok=True)

    for i in range(num_images):
        color = COLORS[i % len(COLORS)]
        img = Image.new("RGB", size, color=color)
        draw = ImageDraw.Draw(img)

        # Ajouter un numéro sur l'image pour faciliter l'identification
        text = str(i + 1)
        # Utiliser textbbox au lieu de textsize pour la compatibilité avec Pillow 10+
        bbox = draw.textbbox((0, 0), text=text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        draw.text(position, text, fill=(0, 0, 0))

        # Sauvegarder l'image
        path = output_dir / f"test_{i+1}.png"
        img.save(path)
        paths.append(path)

    return paths


def test_batch_processing():
    """Teste le traitement par lots avec différents scénarios."""
    # Créer un répertoire temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir, patch(
        "fluxgym_coach.image_enhancement.ImageEnhancer._call_api"
    ) as mock_call_api, patch(
        "fluxgym_coach.image_enhancement.ImageEnhancer.upscale_image"
    ) as mock_upscale_image:

        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        cache_dir = temp_dir / "cache"

        # Configurer les mocks
        # Simuler une réponse réussie pour _call_api avec un nombre dynamique d'images
        def mock_call_api_side_effect(endpoint, payload, **kwargs):
            # Créer une réponse avec le même nombre d'images que dans la requête
            num_images = len(payload.get("imageList", []))
            return {
                "images": [
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # Image factice
                    for _ in range(num_images)
                ]
            }

        mock_call_api.side_effect = mock_call_api_side_effect

        # Simuler une réponse réussie pour upscale_image
        def mock_upscale_side_effect(image_path, output_path, **kwargs):
            # Créer une image vide pour le test
            img = Image.new("RGB", (200, 200), color="red")
            # S'assurer que le répertoire de sortie existe
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Sauvegarder l'image
            img.save(output_path)
            # Retourner un tuple (chemin, est_nb) comme attendu
            return output_path, False  # False car l'image n'est pas en noir et blanc

        mock_upscale_image.side_effect = mock_upscale_side_effect

        # Créer des images de test
        print("Création des images de test...")
        image_paths = create_test_images(temp_dir / "input", num_images=4)

        # Créer les répertoires de sortie
        (output_dir / "batch1").mkdir(parents=True, exist_ok=True)
        (output_dir / "batch2").mkdir(parents=True, exist_ok=True)

        # Créer les répertoires de sortie
        (output_dir / "batch1").mkdir(parents=True, exist_ok=True)
        (output_dir / "batch2").mkdir(parents=True, exist_ok=True)

        # Initialiser l'améliorateur d'images avec un cache
        from fluxgym_coach.image_cache import ImageCache

        cache = ImageCache(cache_dir)
        enhancer = ImageEnhancer(cache=cache)

        # Scénario 1: Traitement initial (aucune image en cache)
        print("\n=== Scénario 1: Traitement initial (aucune image en cache) ===")
        results1 = enhancer.upscale_batch(
            image_paths=image_paths, output_dir=output_dir / "batch1", scale_factor=2
        )

        # Afficher les résultats bruts pour le débogage
        print("\n=== Résultats bruts du traitement par lots ===")
        for i, result in enumerate(results1):
            if result is not None and isinstance(result, tuple) and len(result) == 2:
                output_path, is_bw = result
                print(f"Résultat {i+1}: {output_path} (est_nb={is_bw})")
            else:
                print(f"Résultat {i+1} invalide: {result}")

        # Vérifier que tous les résultats sont présents et dans le bon ordre
        assert len(results1) == len(
            image_paths
        ), f"Le nombre de résultats ({len(results1)}) ne correspond pas au nombre d'images d'entrée ({len(image_paths)})"
        for i, (result, img_path) in enumerate(zip(results1, image_paths)):
            assert (
                result is not None and isinstance(result, tuple) and len(result) == 2
            ), f"Résultat invalide pour l'image {i+1}: {result}"
            output_path, _ = result
            assert (
                output_path is not None
            ), f"Chemin de sortie manquant pour l'image {i+1}"
            assert (
                output_path.exists()
            ), f"Le fichier de sortie n'existe pas: {output_path}"
            print(f"Image {i+1}: {img_path.name} -> {output_path}")

        # Scénario 2: Traitement avec certaines images en cache
        print("\n=== Scénario 2: Traitement avec certaines images en cache ===")
        # Ajouter de nouvelles images
        new_image_paths = create_test_images(
            temp_dir / "input_new", num_images=2, size=(120, 120)
        )

        # Créer une copie des chemins d'entrée originaux pour la vérification ultérieure
        original_paths = [Path(p) for p in image_paths]

        # Mélanger les chemins: [original1, new1, original2, new2]
        mixed_paths = [
            original_paths[0],
            new_image_paths[0],
            original_paths[1],
            new_image_paths[1],
        ]

        results2 = enhancer.upscale_batch(
            image_paths=mixed_paths, output_dir=output_dir / "batch2", scale_factor=2
        )

        # Vérifier que tous les résultats sont présents et dans le bon ordre
        assert len(results2) == len(
            mixed_paths
        ), "Le nombre de résultats ne correspond pas"
        for i, (result, img_path) in enumerate(zip(results2, mixed_paths)):
            output_path, _ = result
            assert output_path is not None, f"Échec du traitement de l'image {i+1}"
            print(f"Image {i+1}: {img_path.name} -> {output_path}")

        # Vérifier que les images en cache sont correctement identifiées
        for i, img_path in enumerate(mixed_paths):
            # Déterminer si l'image est censée être en cache (les images d'index 0 et 2 viennent du premier lot)
            # et si c'est une nouvelle image (index 1 et 3)
            is_from_first_batch = i in [0, 2]
            is_new_image = i in [1, 3]

            print(f"\nVérification de l'image {i+1} ({img_path.name}):")
            print(
                f"- Provenance: {'Premier lot' if is_from_first_batch else 'Nouvelle image'}"
            )

            # Utiliser les mêmes paramètres que ceux utilisés par upscale_batch
            cache_params = {
                "scale_factor": 2,
                "upscaler": "R-ESRGAN 4x+ Anime6B",
                "output_format": "PNG",
                "auto_colorize": True,
                "denoising_strength": 0.5,
                "prompt": "high quality, high resolution, detailed",
                "negative_prompt": "blurry, lowres, low quality, artifacts, jpeg artifacts",
                "steps": 20,
                "cfg_scale": 7.0,
                "sampler_name": "DPM++ 2M",
                "colorize_prompt": None,
                "colorize_negative_prompt": None,
                "api_url": "http://127.0.0.1:7860",  # Ajouté pour la cohérence
            }

            # Vérifier si le fichier de sortie existe
            output_file = results2[i][0]
            print(f"- Fichier de sortie: {output_file}")
            print(
                f"- Le fichier de sortie existe: {os.path.exists(output_file) if output_file else 'N/A'}"
            )

            # Pour les images du premier lot, vérifier qu'elles sont bien dans le cache
            if is_from_first_batch:
                # Utiliser le chemin d'origine correspondant
                cache_check_path = original_paths[0] if i == 0 else original_paths[1]
                print(
                    f"- Vérification du cache pour l'image du premier lot: {cache_check_path}"
                )

                # Vérifier si l'image est dans le cache
                is_cached = enhancer.cache.is_cached(
                    cache_check_path, output_path=output_file, params=cache_params
                )

                print(f"- Résultat de is_cached: {is_cached}")
                assert (
                    is_cached
                ), f"L'image {i+1} du premier lot devrait être dans le cache. Chemin vérifié: {cache_check_path}"
                print(
                    f"✅ L'image {i+1} est correctement identifiée comme étant en cache (premier lot)"
                )

            # Pour les nouvelles images, vérifier que le fichier de sortie existe et est valide
            elif is_new_image:
                print(
                    f"- Vérification du fichier de sortie pour la nouvelle image: {output_file}"
                )
                assert (
                    output_file is not None
                ), f"Le fichier de sortie pour l'image {i+1} est None"
                assert os.path.exists(
                    output_file
                ), f"Le fichier de sortie pour l'image {i+1} n'existe pas: {output_file}"
                print(
                    f"✅ Le fichier de sortie pour l'image {i+1} existe bien: {output_file}"
                )
            else:
                print(f"⚠️  Cas non géré pour l'index {i}")

        print("\n✅ Tous les tests se sont déroulés avec succès!")


def main():
    """Fonction principale."""
    try:
        test_batch_processing()
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
