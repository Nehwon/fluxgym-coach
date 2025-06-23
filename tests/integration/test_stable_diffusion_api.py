"""Tests d'intégration pour l'API Stable Diffusion."""

import base64
import io
import json
import os
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from unittest.mock import MagicMock, patch

import pytest
import requests
from PIL import Image

from fluxgym_coach.image_enhancement import ImageEnhancer

# Constantes pour les tests
TEST_IMAGE_PATH = Path("tests/test_data/test_image.png")
MOCK_API_URL = "http://localhost:9999"  # URL factice pour les tests


class TestStableDiffusionAPI:
    """Tests d'intégration pour l'API Stable Diffusion."""

    @pytest.fixture
    def mock_api_response(self):
        """Fixture pour simuler les réponses de l'API Stable Diffusion."""
        # Création d'une image de test
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        # Configuration de la réponse simulée
        mock_response = {
            'images': [img_base64],
            'parameters': {},
            'info': 'test info'
        }
        
        with patch('requests.Session.send') as mock_send:
            # Configuration du mock pour simuler une réponse réussie
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.text = json.dumps(mock_response)
            mock_http_response.json.return_value = mock_response
            mock_send.return_value = mock_http_response
            
            yield mock_send

    def test_upscale_image_success(self, mock_api_response):
        """Test la fonction d'upscaling avec succès."""
        # Initialisation
        enhancer = ImageEnhancer(api_url=MOCK_API_URL, use_cache=False)
        
        # Création d'un fichier image temporaire pour le test
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp_file, format='PNG')
            test_image_path = tmp_file.name
        
        try:
            # Appel de la méthode à tester
            output_path, is_bw = enhancer.upscale_image(
                image_path=Path(test_image_path),
                scale_factor=2,
                upscaler="R-ESRGAN 4x+ Anime6B",
                denoising_strength=0.5,
                prompt="high quality, high resolution, detailed",
                negative_prompt="blurry, lowres, low quality",
                steps=20,
                cfg_scale=7.0,
                sampler_name="DPM++ 2M",
                output_format='PNG',
                auto_colorize=True
            )
        finally:
            # Nettoyage
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)
        
        # Vérifications
        assert output_path is not None
        assert isinstance(output_path, Path)
        assert isinstance(is_bw, bool)
        
        # Vérification que l'API a été appelée deux fois (colorisation + upscaling)
        assert mock_api_response.call_count == 2
        
        # Vérification du premier appel API (colorisation)
        first_call_args = mock_api_response.call_args_list[0][0][0]
        assert first_call_args.method == 'POST'
        assert f"{MOCK_API_URL}/sdapi/v1/img2img" in first_call_args.url
        
        # Vérification du corps de la première requête (colorisation)
        first_request_data = json.loads(first_call_args.body)
        assert 'init_images' in first_request_data
        assert 'colorized' in first_request_data.get('prompt', '').lower()
        
        # Vérification du deuxième appel API (upscaling)
        second_call_args = mock_api_response.call_args_list[1][0][0]
        assert second_call_args.method == 'POST'
        assert f"{MOCK_API_URL}/sdapi/v1/img2img" in second_call_args.url
        
        # Vérification du corps de la deuxième requête (upscaling)
        second_request_data = json.loads(second_call_args.body)
        assert 'init_images' in second_request_data
        assert second_request_data.get('hr_scale') == 2  # Vérification du facteur d'échelle
        assert second_request_data.get('hr_upscaler') == "R-ESRGAN 4x+ Anime6B"
        assert second_request_data.get('denoising_strength') == 0.5
        assert second_request_data.get('prompt') == "high quality, high resolution, detailed"


    def test_colorize_image_success(self, mock_api_response):
        """Test la fonction de colorisation avec succès."""
        # Initialisation
        enhancer = ImageEnhancer(api_url=MOCK_API_URL, use_cache=False)
        
        # Création d'une image de test
        test_image = Image.new('L', (100, 100), color='white')  # Image en niveaux de gris
        
        # Appel de la méthode à tester
        result = enhancer.colorize_image(
            image=test_image,
            prompt="high quality, high resolution, detailed, colorized",
            negative_prompt="black and white, grayscale, blurry, lowres, low quality",
            steps=30,
            cfg_scale=7.0,
            sampler_name="DPM++ 2M"
        )
        
        # Vérifications
        assert result is not None
        assert isinstance(result, Image.Image)
        
        # Vérification que l'API a été appelée avec les bons paramètres
        mock_api_response.assert_called_once()
        
        # Vérification des données envoyées à l'API
        call_args = mock_api_response.call_args[0][0]
        assert 'sdapi/v1/img2img' in call_args.url  # Note: corrigé de txt2img à img2img

    def test_api_error_handling(self):
        """Test la gestion des erreurs de l'API."""
        with patch('requests.Session.send') as mock_send, \
             patch('json.loads') as mock_json_loads:
            # Configuration du mock pour simuler une erreur 500
            mock_http_response = MagicMock()
            mock_http_response.status_code = 500
            mock_http_response.raise_for_status.side_effect = requests.HTTPError("Erreur serveur")
            mock_send.return_value = mock_http_response
            mock_json_loads.side_effect = json.JSONDecodeError("Erreur de décodage", doc="", pos=0)
            
            # Initialisation
            enhancer = ImageEnhancer(api_url=MOCK_API_URL, use_cache=False)
            
            # Création d'un fichier image temporaire pour le test
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img = Image.new('RGB', (100, 100), color='white')
                img.save(tmp_file, format='PNG')
                test_image_path = tmp_file.name
            
            try:
                # Vérification que l'exception est levée
                with pytest.raises(URLError):
                    enhancer.upscale_image(
                        image_path=Path(test_image_path),
                        scale_factor=2,
                        upscaler="R-ESRGAN 4x+ Anime6B"
                    )
            finally:
                # Nettoyage
                if os.path.exists(test_image_path):
                    os.unlink(test_image_path)

    def test_timeout_handling(self):
        """Test la gestion des timeouts de l'API."""
        with patch('requests.Session.send') as mock_send, \
             patch('json.loads') as mock_json_loads:
            # Configuration du mock pour simuler un timeout
            mock_send.side_effect = requests.Timeout("Timeout de la requête")
            mock_json_loads.side_effect = json.JSONDecodeError("Timeout", doc="", pos=0)
            
            # Initialisation
            enhancer = ImageEnhancer(api_url=MOCK_API_URL, use_cache=False)
            
            # Création d'un fichier image temporaire pour le test
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img = Image.new('RGB', (100, 100), color='white')
                img.save(tmp_file, format='PNG')
                test_image_path = tmp_file.name
            
            try:
                # Vérification que l'exception est levée
                with pytest.raises(URLError):
                    enhancer.upscale_image(
                        image_path=Path(test_image_path),
                        scale_factor=2,
                        upscaler="R-ESRGAN 4x+ Anime6B"
                    )
            finally:
                # Nettoyage
                if os.path.exists(test_image_path):
                    os.unlink(test_image_path)
