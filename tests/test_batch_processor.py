"""Tests pour le module de traitement par lots d'images."""

import base64
import io
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image, ImageDraw

from fluxgym_coach.batch_processor import BatchProcessor


def create_test_image(width=100, height=100, color=(255, 0, 0), text="Test"):
    """Crée une image de test avec une couleur unie et du texte."""
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, fill=(255, 255, 255))
    return img


def image_to_base64(image):
    """Convertit une image PIL en base64."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


class TestBatchProcessor:
    """Tests pour la classe BatchProcessor."""

    @pytest.fixture
    def batch_processor(self):
        """Instance de BatchProcessor pour les tests."""
        return BatchProcessor(api_url="http://test-server:7860")

    @pytest.fixture
    def test_images(self, tmp_path):
        """Crée des images de test et retourne leurs chemins."""
        img1_path = tmp_path / "test1.png"
        img2_path = tmp_path / "test2.png"
        
        # Créer deux images différentes
        img1 = create_test_image(color=(255, 0, 0), text="Image 1")
        img2 = create_test_image(color=(0, 0, 255), text="Image 2")
        
        # Sauvegarder les images
        img1.save(img1_path, "PNG")
        img2.save(img2_path, "PNG")
        
        return [img1_path, img2_path]

    def test_generate_output_path(self, batch_processor, tmp_path):
        """Teste la génération de chemins de sortie uniques."""
        input_path = tmp_path / "test.png"
        output_path1 = batch_processor._generate_output_path(input_path, tmp_path)
        output_path2 = batch_processor._generate_output_path(input_path, tmp_path)
        
        # Vérifier que les chemins sont différents
        assert output_path1 != output_path2
        # Vérifier que le répertoire de sortie est correct
        assert output_path1.parent == Path(tmp_path)
        # Vérifier le format du nom de fichier
        assert "test_enhanced_" in str(output_path1)
        assert output_path1.suffix == ".png"

    def test_save_image(self, batch_processor, tmp_path):
        """Teste la sauvegarde d'une image encodée en base64."""
        # Créer une image de test
        img = create_test_image()
        img_base64 = image_to_base64(img)
        
        # Chemin de sortie
        output_path = tmp_path / "output.png"
        
        # Sauvegarder l'image
        batch_processor._save_image(img_base64, output_path)
        
        # Vérifier que le fichier a été créé
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Vérifier que c'est une image valide
        with Image.open(output_path) as saved_img:
            assert saved_img.size == (100, 100)

    @patch('requests.post')
    def test_process_batch_success(self, mock_post, batch_processor, test_images, tmp_path):
        """Teste le traitement par lots avec succès."""
        # Créer des images de test avec des dimensions connues
        test_image1 = create_test_image(width=100, height=100, color=(255, 0, 0), text="1")
        test_image2 = create_test_image(width=150, height=150, color=(0, 0, 255), text="2")
        
        # Préparer la réponse simulée de l'API avec des images de sortie agrandies
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "images": [
                image_to_base64(create_test_image(width=200, height=200, color=(255, 0, 0))),
                image_to_base64(create_test_image(width=300, height=300, color=(0, 0, 255)))
            ],
            "parameters": {}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Appeler la méthode à tester avec un facteur d'échelle de 2
        scale_factor = 2
        results = batch_processor.process_batch(
            image_paths=test_images,
            output_dir=tmp_path,
            scale_factor=scale_factor
        )
        
        # Vérifier les résultats
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # Vérifier que les fichiers de sortie ont été créés
        output_files = list(tmp_path.glob('*_enhanced_*.png'))
        assert len(output_files) == 2, f"Expected 2 output files, found {len(output_files)}: {output_files}"
        
        # Vérifier que les chemins de retour correspondent aux fichiers créés
        for i, (result, expected_size) in enumerate(zip(results, [(200, 200), (300, 300)])):
            output_path, is_bw = result
            
            # Vérifier que le chemin de sortie est défini
            assert output_path is not None, f"Output path is None for result {i}"
            
            # Vérifier que le fichier existe
            assert output_path.exists(), f"Output file does not exist: {output_path}"
            
            # Vérifier l'extension du fichier
            assert output_path.suffix == '.png', f"Expected .png file, got {output_path.suffix}"
            
            # Vérifier les dimensions de l'image générée
            with Image.open(output_path) as img:
                assert img.size == expected_size, \
                    f"Expected size {expected_size}, got {img.size} for {output_path.name}"
                
                # Vérifier que l'image n'est pas vide
                assert img.getbbox() is not None, f"Image is empty: {output_path}"
                
                # Vérifier le mode de l'image (doit être RGB ou RGBA)
                assert img.mode in ['RGB', 'RGBA'], f"Unexpected image mode: {img.mode}"
        
        # Vérifier que l'API a été appelée avec les bons paramètres
        assert mock_post.called, "API was not called"
        
        # Vérifier que l'URL de l'API est correcte
        called_url = mock_post.call_args[0][0]
        assert called_url == f"{batch_processor.api_url}/sdapi/v1/extra-batch-images", \
            f"Unexpected API URL: {called_url}"
            
        # Vérifier que le payload contient les bons paramètres
        payload = mock_post.call_args[1]['json']
        assert payload['upscaling_resize'] == float(scale_factor)
        assert len(payload['imageList']) == 2, "Expected 2 images in the payload"

    @patch('requests.post')
    def test_process_batch_api_error(self, mock_post, batch_processor, test_images, tmp_path):
        """Teste la gestion des erreurs d'API lors du traitement par lots."""
        # Simuler une erreur d'API
        mock_post.side_effect = Exception("API Error")
        
        # Créer un sous-répertoire pour les sorties pour éviter les faux positifs
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Appeler la méthode à tester
        results = batch_processor.process_batch(
            image_paths=test_images,
            output_dir=output_dir
        )
        
        # Vérifier que tous les résultats indiquent un échec
        assert len(results) == len(test_images), \
            f"Expected {len(test_images)} results, got {len(results)}"
            
        for result in results:
            assert result[0] is None, "Expected None for output path on API error"
            assert result[1] is False, "Expected is_bw to be False on API error"
            
        # Vérifier qu'aucun fichier de sortie n'a été créé
        # (les fichiers d'entrée sont dans tmp_path, pas dans output_dir)
        output_files = list(output_dir.glob('*'))
        assert len(output_files) == 0, \
            f"Expected no output files, but found: {output_files}"

    def test_process_batch_invalid_image(self, batch_processor, tmp_path):
        """Teste le traitement avec des images invalides."""
        # Créer un sous-répertoire pour les sorties
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Créer un fichier qui n'est pas une image
        invalid_path = tmp_path / "not_an_image.txt"
        with open(invalid_path, 'w') as f:
            f.write("Ceci n'est pas une image")
    
        # Chemin d'une image qui n'existe pas
        non_existent_path = tmp_path / "nonexistent.png"
    
        # Appeler la méthode à tester
        results = batch_processor.process_batch(
            image_paths=[invalid_path, non_existent_path],
            output_dir=output_dir
        )
    
        # Vérifier que nous avons bien 2 résultats (un pour chaque entrée)
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # Vérifier les résultats pour chaque cas
        # 1. Fichier non image (doit échouer avec None, False)
        assert results[0][0] is None, "Expected None for invalid image path"
        assert results[0][1] is False, "Expected is_bw to be False for invalid image"
        
        # 2. Fichier inexistant (doit être ignoré et retourner None, False)
        assert results[1][0] is None, "Expected None for non-existent file"
        assert results[1][1] is False, "Expected is_bw to be False for non-existent file"
            
        # Vérifier qu'aucun fichier de sortie n'a été créé
        output_files = list(output_dir.glob('*'))
        assert len(output_files) == 0, \
            f"Expected no output files, but found: {output_files}"
            
        # Vérifier que les messages d'erreur appropriés ont été enregistrés
        # (peut être vérifié via les logs capturés si nécessaire)
