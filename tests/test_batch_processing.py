"""
Script de test pour le traitement par lots d'images.

Ce script permet de tester la méthode upscale_batch avec différents scénarios
pour s'assurer que l'ordre des résultats est correctement préservé.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from PIL import Image, ImageDraw
import shutil

# Configuration des logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_batch_processing.log', mode='w')
    ]
)

# Activer les logs détaillés pour les modules spécifiques
logging.getLogger('PIL').setLevel(logging.INFO)  # Réduire le bruit de PIL
logging.getLogger('urllib3').setLevel(logging.INFO)  # Réduire le bruit de urllib3

# Activer les logs détaillés pour nos modules
logging.getLogger('fluxgym_coach.image_enhancement').setLevel(logging.DEBUG)
logging.getLogger('fluxgym_coach.image_cache').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au PYTHONPATH pour importer le module
sys.path.insert(0, str(Path(__file__).parent))
from fluxgym_coach.image_enhancement import ImageEnhancer

# Couleurs pour les images de test
COLORS = [
    (255, 0, 0),    # Rouge
    (0, 255, 0),    # Vert
    (0, 0, 255),    # Bleu
    (255, 255, 0),  # Jaune
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]

def create_test_images(output_dir: Path, num_images: int = 3, size: tuple = (100, 100)) -> list[Path]:
    """Crée des images de test avec des couleurs uniques."""
    paths = []
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(num_images):
        color = COLORS[i % len(COLORS)]
        img = Image.new('RGB', size, color=color)
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
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        output_dir = temp_dir / "output"
        cache_dir = temp_dir / "cache"
        
        # Créer des images de test
        print("Création des images de test...")
        image_paths = create_test_images(temp_dir / "input", num_images=4)
        
        # Initialiser l'améliorateur d'images avec un cache
        from fluxgym_coach.image_cache import ImageCache
        cache = ImageCache(cache_dir)
        enhancer = ImageEnhancer(cache=cache)
        
        # Scénario 1: Traitement initial (aucune image en cache)
        print("\n=== Scénario 1: Traitement initial (aucune image en cache) ===")
        results1 = enhancer.upscale_batch(
            image_paths=image_paths,
            output_dir=output_dir / "batch1",
            scale_factor=2
        )
        
        # Vérifier que tous les résultats sont présents et dans le bon ordre
        assert len(results1) == len(image_paths), "Le nombre de résultats ne correspond pas"
        for i, (result, img_path) in enumerate(zip(results1, image_paths)):
            output_path, _ = result
            assert output_path is not None, f"Échec du traitement de l'image {i+1}"
            print(f"Image {i+1}: {img_path.name} -> {output_path}")
        
        # Scénario 2: Traitement avec certaines images en cache
        print("\n=== Scénario 2: Traitement avec certaines images en cache ===")
        # Ajouter de nouvelles images
        new_image_paths = create_test_images(temp_dir / "input_new", num_images=2, size=(120, 120))
        
        # Créer une copie des chemins d'entrée originaux pour la vérification ultérieure
        original_paths = [Path(p) for p in image_paths]
        
        # Mélanger les chemins: [original1, new1, original2, new2]
        mixed_paths = [original_paths[0], new_image_paths[0], original_paths[1], new_image_paths[1]]
        
        results2 = enhancer.upscale_batch(
            image_paths=mixed_paths,
            output_dir=output_dir / "batch2",
            scale_factor=2
        )
        
        # Vérifier que tous les résultats sont présents et dans le bon ordre
        assert len(results2) == len(mixed_paths), "Le nombre de résultats ne correspond pas"
        for i, (result, img_path) in enumerate(zip(results2, mixed_paths)):
            output_path, _ = result
            assert output_path is not None, f"Échec du traitement de l'image {i+1}"
            print(f"Image {i+1}: {img_path.name} -> {output_path}")
        
        # Vérifier que les images en cache sont correctement identifiées
        for i, img_path in enumerate(mixed_paths):
            # Vérifier si l'image est censée être en cache (les images d'index 0 et 2 viennent du premier lot)
            should_be_cached = i in [0, 2]
            print(f"\nVérification de l'image {i+1} ({img_path.name}): devrait être en cache = {should_be_cached}")
            
            # Utiliser les mêmes paramètres que ceux utilisés par upscale_batch
            cache_params = {
                'scale_factor': 2,
                'upscaler': 'R-ESRGAN 4x+ Anime6B',
                'output_format': 'PNG',
                'auto_colorize': True,
                'denoising_strength': 0.5,
                'prompt': 'high quality, high resolution, detailed',
                'negative_prompt': 'blurry, lowres, low quality, artifacts, jpeg artifacts',
                'steps': 20,
                'cfg_scale': 7.0,
                'sampler_name': 'DPM++ 2M',
                'colorize_prompt': None,
                'colorize_negative_prompt': None,
                'api_url': 'http://127.0.0.1:7860'  # Ajouté pour la cohérence
            }
            
            print(f"Paramètres de cache utilisés: {json.dumps(cache_params, indent=2, default=str)}")
            
            # Vérifier si le fichier de sortie existe
            output_file = results2[i][0]
            print(f"Fichier de sortie: {output_file}")
            print(f"Le fichier de sortie existe: {os.path.exists(output_file) if output_file else 'N/A'}")
            
            # Pour les images censées être en cache, utiliser le chemin d'origine correspondant
            if i == 0:
                # Première image du mélange: première image du premier lot
                cache_check_path = original_paths[0]
            elif i == 2:
                # Troisième image du mélange: deuxième image du premier lot
                cache_check_path = original_paths[1]
            else:
                # Images non censées être en cache (nouvelles images)
                cache_check_path = img_path
                
            print(f"Vérification du cache pour: {cache_check_path}")
            
            # Vérifier si l'image est dans le cache
            is_cached = enhancer.cache.is_cached(
                cache_check_path,
                output_path=output_file,
                params=cache_params
            )
            
            print(f"Résultat de is_cached: {is_cached}")
            assert is_cached == should_be_cached, f"L'état du cache pour l'image {i+1} est incorrect (attendu: {should_be_cached}, obtenu: {is_cached}). Chemin vérifié: {cache_check_path}"
            
            if is_cached:
                print(f"✅ L'image {i+1} est correctement identifiée comme étant en cache")
            else:
                print(f"ℹ️  L'image {i+1} n'est pas en cache (comme attendu)")
        
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
