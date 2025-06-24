"""
Module pour l'amélioration d'images avec Stable Diffusion Forge.
Permet d'augmenter la résolution et d'améliorer la qualité des images.
"""

import base64
import io
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast, Set
from urllib.error import URLError

import requests
from PIL import Image, ImageFilter, ImageOps, Image as PILImage

from .image_cache import ImageCache, get_default_cache

# Configuration du logger
logger = logging.getLogger(__name__)

# Constantes pour la compatibilité avec différentes versions de Pillow
try:
    RESAMPLING = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLING = Image.LANCZOS  # type: ignore[attr-defined]  # Pour les anciennes versions

# Constantes
MIN_WIDTH = 1024  # Largeur minimale pour le redimensionnement
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}

class ImageEnhancer:
    """Classe pour améliorer des images via l'API Stable Diffusion Forge."""
    
    def __init__(
        self, 
        api_url: str = "http://127.0.0.1:7860",
        cache: Optional[ImageCache] = None,
        use_cache: bool = True
    ):
        """
        Initialise l'améliorateur d'images avec l'URL de l'API et le cache.
        
        Args:
            api_url: URL de l'API Stable Diffusion WebUI (par défaut: http://127.0.0.1:7860)
            cache: Instance de ImageCache à utiliser (par défaut: instance partagée)
            use_cache: Si False, désactive complètement le cache
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = 300  # 5 minutes de timeout pour les requêtes
        self.use_cache = use_cache
        self.cache = cache if cache is not None else get_default_cache()
        self._processed_paths: Set[Path] = set()  # Pour éviter les doublons dans un même traitement
        
    def _call_api(self, endpoint: str, payload: Dict[str, Any], max_retries: int = 4, initial_delay: float = 1.0) -> Dict[str, Any]:
        """
        Effectue un appel à l'API Stable Diffusion Forge avec mécanisme de réessai.
        
        Args:
            endpoint: Point de terminaison de l'API (ex: 'sdapi/v1/txt2img')
            payload: Données à envoyer à l'API
            max_retries: Nombre maximum de tentatives (défaut: 4)
            initial_delay: Délai initial avant la première tentative (en secondes, défaut: 1.0)
            
        Returns:
            Réponse de l'API sous forme de dictionnaire
            
        Raises:
            URLError: Si toutes les tentatives échouent
            json.JSONDecodeError: Si la réponse n'est pas du JSON valide
        """
        url = f"{self.api_url}/{endpoint}"
        data = json.dumps(payload).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Tentative {attempt + 1}/{max_retries} - Appel de l'API à {url}...")
                response = requests.post(
                    url,
                    data=data,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # Gestion des erreurs HTTP (comme 404, 500, etc.)
                status_code = getattr(e.response, 'status_code', 'inconnu')
                reason = getattr(e.response, 'reason', 'Raison inconnue')
                
                # Essayer d'extraire plus de détails de la réponse d'erreur
                error_details = {}
                try:
                    error_response = e.response.json()
                    if isinstance(error_response, dict):
                        error_details = {
                            'detail': error_response.get('detail'),
                            'validation_error': error_response.get('validation_error'),
                            'message': error_response.get('message')
                        }
                except (ValueError, AttributeError):
                    try:
                        error_details = {'response_text': e.response.text[:500] + '...' if e.response.text else 'Aucun détail supplémentaire'}
                    except:
                        error_details = {'error': 'Impossible de récupérer les détails de l\'erreur'}
                
                error_msg = f"Erreur HTTP {status_code} lors de l'appel à {url}: {reason}"
                if error_details:
                    error_msg += f"\nDétails de l'erreur: {json.dumps(error_details, indent=2, ensure_ascii=False)}"
                
                logger.error(error_msg)
                last_exception = e
                
                # Si c'est une erreur 422 (Unprocessable Entity), on arrête les tentatives
                if status_code == 422:
                    logger.error("Erreur de validation des données. Arrêt des tentatives.")
                    raise URLError(error_msg) from e
                
                # Ne pas réessayer pour les erreurs client (4xx) sauf 429 (Too Many Requests)
                if 400 <= status_code < 500 and status_code != 429:
                    logger.error(f"Erreur client: {error_msg}")
                    break
                    
                logger.warning(f"{error_msg} - Tentative {attempt + 1}/{max_retries}")
                
            except (requests.exceptions.RequestException, ConnectionError) as e:
                # Gestion des erreurs de connexion, timeout, etc.
                error_msg = f"Erreur de connexion à {url}: {str(e)}"
                last_exception = e
                logger.warning(f"{error_msg} - Tentative {attempt + 1}/{max_retries}")
                # Pour les erreurs 422, on ne réessaie pas car c'est une erreur de validation
                if not (hasattr(last_exception, 'response') and getattr(last_exception.response, 'status_code', None) == 422):
                    # Calculer le délai exponentiel avec un peu d'aléatoire (jitter)
                    delay = min(initial_delay * (2 ** attempt) * (0.8 + 0.4 * random.random()), 60)  # Maximum 60 secondes
                    logger.warning(f"{error_msg} - Nouvelle tentative dans {delay:.1f} secondes...")
                    time.sleep(delay)
                else:
                    logger.error("Erreur de validation des données. Arrêt des tentatives.")
                    break
        
        # Si on arrive ici, toutes les tentatives ont échoué
        logger.error(f"Échec après {max_retries} tentatives")
        if isinstance(last_exception, requests.exceptions.HTTPError):
            status_code = getattr(last_exception.response, 'status_code', 'inconnu')
            reason = getattr(last_exception.response, 'reason', 'Raison inconnue')
            error_msg = f"Erreur HTTP {status_code} lors de l'appel à {url}: {reason}"
            raise URLError(error_msg) from last_exception
        else:
            error_msg = f"Impossible de se connecter à l'API à {url} après {max_retries} tentatives"
            if last_exception:
                error_msg += f": {str(last_exception)}"
            raise URLError(error_msg) from last_exception
    
    def preprocess_image(
        self, 
        image_path: Union[str, Path],
        output_format: str = 'PNG'
    ) -> Tuple[Image.Image, bool]:
        """
        Prétraite une image : conversion de format et redimensionnement.
        
        Args:
            image_path: Chemin vers l'image source
            output_format: Format de sortie (par défaut: 'PNG')
            
        Returns:
            Tuple contenant l'image prétraitée et un booléen indiquant si l'image est en N&B
            
        Raises:
            FileNotFoundError: Si le fichier image n'existe pas
            ValueError: Si le format de sortie n'est pas pris en charge
        """
        if output_format.upper() not in {'PNG', 'JPEG', 'WEBP'}:
            raise ValueError("Format de sortie non pris en charge. Utilisez 'PNG', 'JPEG' ou 'WEBP'")
            
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Le fichier {image_path} n'existe pas")
            
        # Charger l'image
        try:
            with Image.open(image_path) as img:
                # Convertir en RGB si nécessaire (pour les images avec canal alpha)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Vérifier si l'image est en noir et blanc
                is_bw = self._is_black_and_white(img)
                
                # Redimensionner l'image si nécessaire
                if img.width < MIN_WIDTH:
                    new_height = int((MIN_WIDTH / img.width) * img.height)
                    img = img.resize((MIN_WIDTH, new_height), RESAMPLING)
                
                return img, is_bw
                
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement de l'image {image_path}: {e}")
            raise
    
    def _is_black_and_white(self, image: Image.Image, threshold: float = 5.0) -> bool:
        """
        Détermine si une image est en noir et blanc.
        
        Args:
            image: Image à analyser
            threshold: Seuil de tolérance pour la détection de N&B (en %)
            
        Returns:
            True si l'image est en noir et blanc, False sinon
        """
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Obtenir les données des pixels
        pixels = list(image.getdata())
        total_pixels = len(pixels)
        if total_pixels == 0:
            return True
            
        # Compter les pixels qui ne sont pas en niveaux de gris
        color_pixels = 0
        
        for r, g, b in pixels:
            # Calculer la différence maximale entre les canaux
            max_diff = max(abs(r - g), abs(g - b), abs(r - b))
            # Si la différence est supérieure au seuil, c'est un pixel coloré
            if max_diff > 1:  # Seuil de différence de couleur
                color_pixels += 1
                
        # Calculer le pourcentage de pixels en couleur
        color_ratio = (color_pixels / total_pixels) * 100
        
        # Si moins de 'threshold' % des pixels sont en couleur, considérer l'image comme N&B
        return color_ratio < threshold
    
    def encode_image_to_base64(self, image: Image.Image, format: str = 'PNG') -> str:
        """
        Encode une image PIL en base64.
        
        Args:
            image: Image PIL à encoder
            format: Format de sortie (ignoré, toujours converti en PNG)
            
        Returns:
            Chaîne encodée en base64
        """
        buffered = io.BytesIO()
        # Toujours convertir en PNG pour éviter les problèmes avec certains formats
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        image.save(buffered, format='PNG', quality=95)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def decode_and_save_base64(
        self, 
        base64_str: str, 
        output_path: Union[str, Path],
        overwrite: bool = False
    ) -> None:
        """
        Décode une image en base64 et l'enregistre sur le disque.
        
        Args:
            base64_str: Image encodée en base64
            output_path: Chemin de sortie pour l'image décodée
            overwrite: Écraser le fichier s'il existe déjà
            
        Raises:
            FileExistsError: Si le fichier existe déjà et que overwrite est False
        """
        output_path = Path(output_path)
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Le fichier {output_path} existe déjà")
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as file:
            file.write(base64.b64decode(base64_str))
    
    def colorize_image(
        self,
        image: Image.Image,
        prompt: str = "high quality, high resolution, detailed, colorized",
        negative_prompt: str = "black and white, grayscale, blurry, lowres, low quality",
        steps: int = 30,
        cfg_scale: float = 7.0,
        sampler_name: str = "DPM++ 2M",
    ) -> Image.Image:
        """
        Colorise une image en noir et blanc avec Stable Diffusion Forge.
        
        Args:
            image: Image PIL à coloriser (doit être en noir et blanc)
            prompt: Prompt pour guider la colorisation
            negative_prompt: Éléments à éviter
            steps: Nombre d'étapes de génération
            cfg_scale: Échelle de configuration du classificateur
            sampler_name: Nom de l'échantillonneur à utiliser
            
        Returns:
            Image PIL colorisée
            
        Raises:
            ValueError: Si l'image n'est pas en noir et blanc
            URLError: Si l'appel à l'API échoue
        """
        # Vérifier que l'image est bien en noir et blanc
        if not self._is_black_and_white(image):
            raise ValueError("L'image fournie n'est pas en noir et blanc")
            
        # Encoder l'image
        encoded_image = self.encode_image_to_base64(image, 'PNG')
        
        # Préparer la charge utile pour l'API
        payload = {
            "init_images": [encoded_image],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": sampler_name,
            "denoising_strength": 0.7,  # Force de colorisation plus élevée
            "width": image.width,
            "height": image.height,
            "restore_faces": True,
            "tiling": False,
        }
        
        try:
            # Appel à l'API de colorisation
            response = self._call_api('sdapi/v1/img2img', payload)
            
            # Vérification de la réponse
            if not response.get('images') or not response['images']:
                raise ValueError("Aucune image n'a été retournée par l'API de colorisation")
                
            # Décodage de l'image colorisée
            colorized_data = base64.b64decode(response['images'][0])
            colorized_img = Image.open(io.BytesIO(colorized_data)).convert('RGB')
            
            return colorized_img
            
        except Exception as e:
            logger.error(f"Erreur lors de la colorisation de l'image: {e}")
            raise URLError(f"Échec de la colorisation: {e}")
    
    def _get_output_path(
        self,
        image_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]],
        output_format: str
    ) -> Path:
        """
        Génère un chemin de sortie pour une image.
        
        Args:
            image_path: Chemin de l'image source
            output_dir: Répertoire de sortie (optionnel)
            output_format: Format de sortie
            
        Returns:
            Chemin de sortie complet
        """
        image_path = Path(image_path)
        if output_dir:
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            return output_dir_path / f"{image_path.stem}_enhanced.{output_format.lower()}"
        return image_path.parent / f"{image_path.stem}_enhanced.{output_format.lower()}"
    
    def _get_cache_params(
        self,
        scale_factor: int,
        upscaler: str,
        output_format: str,
        auto_colorize: bool,
        colorize_prompt: Optional[str] = None,
        colorize_negative_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Génère un dictionnaire de paramètres pour le cache.
        
        Args:
            scale_factor: Facteur d'échelle
            upscaler: Nom de l'upscaler
            output_format: Format de sortie
            auto_colorize: Si la colorisation automatique est activée
            colorize_prompt: Prompt pour la colorisation (optionnel)
            colorize_negative_prompt: Prompt négatif pour la colorisation (optionnel)
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Dictionnaire des paramètres pour le cache
        """
        return {
            'scale_factor': scale_factor,
            'upscaler': upscaler,
            'output_format': output_format,
            'auto_colorize': auto_colorize,
            'colorize_prompt': colorize_prompt,
            'colorize_negative_prompt': colorize_negative_prompt,
            'api_url': self.api_url,
            **kwargs
        }
        
    def _process_single_image(
        self,
        image_path: Union[str, Path],
        output_path: Optional[Union[str, Path]],
        params: Dict[str, Any],
        skip_cache: bool = False
    ) -> Tuple[Optional[Path], bool, Optional[str]]:
        """
        Traite une seule image avec gestion du cache.
        
        Args:
            image_path: Chemin vers l'image source
            output_path: Chemin de sortie (optionnel)
            params: Paramètres de traitement
            skip_cache: Si True, ignore le cache
            
        Returns:
            Tuple (chemin_sortie, est_nb, image_encodée) ou (None, False, None) en cas d'erreur
        """
        try:
            image_path = Path(image_path).resolve()
            
            # Vérifier si l'image a déjà été traitée dans cette session
            if image_path in self._processed_paths:
                logger.debug(f"Image déjà traitée dans cette session: {image_path}")
                return None, False, None
                
            # Vérifier le cache si activé
            if self.use_cache and not skip_cache and self.cache:
                if self.cache.is_cached(image_path, output_path, params):
                    logger.info(f"Image en cache, saut du traitement: {image_path}")
                    self._processed_paths.add(image_path)
                    return Path(output_path) if output_path else None, False, None
            
            # Prétraiter l'image
            output_format = params.get('output_format', 'PNG')
            image, is_bw = self.preprocess_image(image_path, output_format=output_format)
            
            # Si l'image est en N/B et que la colorisation est activée
            if is_bw and params.get('auto_colorize', True):
                logger.info(f"Colorisation de l'image N/B: {image_path}")
                colorized_path = self.colorize_image(
                    image_path=image_path,
                    output_path=output_path,
                    prompt=params.get('colorize_prompt'),
                    negative_prompt=params.get('colorize_negative_prompt'),
                    output_format=output_format
                )
                if colorized_path:
                    image_path = colorized_path
                    image, _ = self.preprocess_image(image_path, output_format=output_format)
                    is_bw = False
            
            # Déterminer le chemin de sortie si non spécifié
            if output_path is None:
                output_path = self._get_output_path(image_path, None, output_format)
            else:
                output_path = Path(output_path).resolve()
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convertir en mode RGB pour éviter les problèmes avec les images en niveaux de gris
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Encoder l'image pour l'API
            buffered = io.BytesIO()
            image.save(buffered, format=output_format)
            encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return output_path, is_bw, encoded_image
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement de {image_path}: {e}")
            return None, False, None
    
    def upscale_batch(
        self,
        image_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        scale_factor: int = 2,
        upscaler: str = "R-ESRGAN 4x+ Anime6B",
        denoising_strength: float = 0.5,
        prompt: str = "high quality, high resolution, detailed",
        negative_prompt: str = "blurry, lowres, low quality, artifacts, jpeg artifacts",
        steps: int = 20,
        cfg_scale: float = 7.0,
        sampler_name: str = "DPM++ 2M",
        output_format: str = 'PNG',
        auto_colorize: bool = True,
        colorize_prompt: Optional[str] = None,
        colorize_negative_prompt: Optional[str] = None,
        force_reprocess: bool = False,
        skip_cache: bool = False
    ) -> List[Tuple[Optional[Path], bool]]:
        """
        Améliore la résolution d'un lot d'images avec gestion du cache.
        
        Args:
            image_paths: Liste des chemins vers les images sources
            output_dir: Répertoire de sortie pour les images améliorées
            scale_factor: Facteur d'échelle (1-4)
            upscaler: Nom de l'upscaler à utiliser
            denoising_strength: Force du débruiteur (0-1)
            prompt: Prompt pour guider l'amélioration
            negative_prompt: Éléments à éviter
            steps: Nombre d'étapes de débruiteur
            cfg_scale: Échelle de configuration du classificateur
            sampler_name: Nom de l'échantillonneur à utiliser
            output_format: Format de sortie des images
            auto_colorize: Si True, tente de coloriser les images en N&B
            colorize_prompt: Prompt personnalisé pour la colorisation (optionnel)
            colorize_negative_prompt: Prompt négatif pour la colorisation (optionnel)
            force_reprocess: Si True, force le retraitement même si l'image est en cache
            skip_cache: Si True, ignore complètement le cache
            
        Returns:
            Liste de tuples (chemin_sortie, est_nb) pour chaque image traitée
            
        Raises:
            ValueError: Si les paramètres sont invalides
            URLError: Si l'appel à l'API échoue
        """
        logger.info(f"Début du traitement par lots de {len(image_paths)} images")
        
        # Validation des entrées
        if not image_paths:
            raise ValueError("Aucune image à traiter")
            
        if not 1 <= scale_factor <= 4:
            raise ValueError("Le facteur d'échelle doit être entre 1 et 4")
            
        if not 0 <= denoising_strength <= 1:
            raise ValueError("La force du débruiteur doit être entre 0 et 1")
        
        # Préparation du répertoire de sortie
        if output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Préparer les paramètres pour le cache
        cache_params = self._get_cache_params(
            scale_factor=scale_factor,
            upscaler=upscaler,
            output_format=output_format,
            auto_colorize=auto_colorize,
            colorize_prompt=colorize_prompt,
            colorize_negative_prompt=colorize_negative_prompt,
            denoising_strength=denoising_strength,
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            cfg_scale=cfg_scale,
            sampler_name=sampler_name
        )
        
        # Initialiser la liste des résultats avec des valeurs par défaut
        results = [(None, False)] * len(image_paths)
        
        # Liste pour stocker les images à traiter
        images_to_process = []
        
        # Vérifier le cache pour chaque image
        for idx, img_path in enumerate(image_paths):
            try:
                img_path = Path(img_path).resolve()
                
                # Vérifier si l'image a déjà été traitée dans cette session
                if str(img_path) in self._processed_paths and not force_reprocess:
                    logger.debug(f"Image déjà traitée dans cette session: {img_path}")
                    continue
                
                # Générer le chemin de sortie
                output_path = self._get_output_path(img_path, output_dir, output_format)
                
                # Vérifier le cache
                if self.use_cache and not skip_cache and self.cache and not force_reprocess:
                    logger.debug(f"[DEBUG] Vérification du cache pour l'image {idx} ({img_path.name})...")
                    logger.debug(f"[DEBUG] Chemin de sortie: {output_path}")
                    logger.debug(f"[DEBUG] Paramètres du cache: {json.dumps(cache_params, indent=2, default=str)}")
                    
                    is_cached = self.cache.is_cached(img_path, output_path, cache_params)
                    logger.debug(f"[DEBUG] Résultat de la vérification du cache pour {img_path.name}: {is_cached}")
                    
                    if is_cached:
                        logger.info(f"[INFO] Image {idx} ({img_path.name}) en cache, saut du traitement: {img_path} -> {output_path}")
                        self._processed_paths.add(str(img_path))
                        results[idx] = (str(output_path), False)  # S'assurer que le chemin est une chaîne
                        logger.debug(f"[DEBUG] Résultat mis à jour à l'index {idx}: {results[idx]}")
                        logger.debug(f"[DEBUG] État actuel des résultats: {results}")
                        continue
                
                # Prétraiter l'image
                processed_img, is_bw = self.preprocess_image(img_path, output_format)
                
                # Gérer les images en noir et blanc
                if is_bw and auto_colorize:
                    try:
                        color_prompt = colorize_prompt or "high quality, high resolution, detailed, colorized, vibrant colors"
                        color_negative = colorize_negative_prompt or "black and white, grayscale, blurry, lowres, low quality"
                        
                        logger.info(f"Colorisation de l'image {img_path.name} détectée en N/B")
                        processed_img = self.colorize_image(
                            image=processed_img,
                            prompt=color_prompt,
                            negative_prompt=color_negative,
                            steps=steps,
                            cfg_scale=cfg_scale,
                            sampler_name=sampler_name
                        )
                        is_bw = False
                    except Exception as colorize_error:
                        logger.warning(f"Échec de la colorisation de l'image {img_path.name}: {colorize_error}")
                        if "black and white" not in prompt.lower() and "monochrome" not in prompt.lower():
                            prompt += ", black and white, monochrome"
                
                # Encoder l'image
                encoded_image = self.encode_image_to_base64(processed_img, output_format)
                
                # Stocker les informations pour le traitement
                images_to_process.append({
                    'original_index': idx,  # Conserver l'index d'origine
                    'path': img_path,
                    'output_path': output_path,
                    'image': encoded_image,
                    'is_bw': is_bw
                })
                
            except Exception as e:
                logger.error(f"Erreur lors du prétraitement de l'image {img_path}: {e}")
                # Garder la valeur par défaut (None, False) pour cette image
                continue
        
        # Si aucune image à traiter, retourner les résultats actuels
        if not images_to_process:
            return results
        
        # Préparer la charge utile pour l'API
        # Format basé sur l'implémentation de sdwebuiapi
        payload = {
            "resize_mode": 0,  # 0 = Just resize (ne pas forcer le carré)
            "show_extras_results": False,
            "gfpgan_visibility": 0.0,
            "codeformer_visibility": 0.0,
            "codeformer_weight": 0.0,
            "upscaling_resize": float(scale_factor),
            "upscaling_resize_w": 1024,  # Largeur cible (sera mise à l'échelle par le facteur)
            "upscaling_resize_h": 1024,  # Hauteur cible (sera mise à l'échelle par le facteur)
            "upscaling_crop": False,  # Ne pas rogner pour conserver les proportions
            "upscaler_1": upscaler,
            "upscaler_2": "None",
            "extras_upscaler_2_visibility": 0.0,
            "upscale_first": False
        }
        
        # Préparer la liste des images au format attendu par l'API
        image_list = []
        for i, img in enumerate(images_to_process):
            if img['image'] is not None:
                # Convertir l'image en base64 sans l'en-tête data:image/...
                if isinstance(img['image'], str) and img['image'].startswith('data:image/'):
                    # Si c'est déjà une chaîne base64 avec en-tête, extraire juste les données
                    base64_data = img['image'].split(',', 1)[1] if ',' in img['image'] else img['image']
                else:
                    # Sinon, utiliser directement les données binaires
                    base64_data = img['image']
                
                image_list.append({
                    "data": base64_data,
                    "name": f"image_{i}.{output_format.lower()}"
                })
        
        # Appel à l'API avec gestion d'erreur améliorée
        try:
            # Ajouter la liste des images au payload
            payload['imageList'] = image_list
            
            # Préparer les données pour le logging (sans les données d'image complètes)
            log_payload = {k: v for k, v in payload.items()}
            if 'imageList' in log_payload:
                log_payload['imageList'] = [{"name": img['name'], "data_length": len(img['data'])} 
                                          for img in log_payload['imageList']]
            
            logger.info(f"Envoi de la requête de traitement par lots pour {len(images_to_process)} images")
            logger.debug(f"Payload de la requête : {json.dumps(log_payload, indent=2)}")
            
            # Appel à l'API
            response = self._call_api('sdapi/v1/extra-batch-images', payload)
            
            # Vérification de la réponse
            if not isinstance(response, dict):
                raise ValueError(f"Réponse API invalide (type {type(response)}): {response}")
                
            if 'error' in response:
                error_msg = response.get('error', 'Erreur inconnue')
                if isinstance(error_msg, dict):
                    error_msg = json.dumps(error_msg, indent=2)
                raise ValueError(f"Erreur de l'API: {error_msg}")
                
            if 'images' not in response or not response['images']:
                raise ValueError(f"Aucune image retournée dans la réponse: {json.dumps(response, indent=2)}")
                
            if len(response['images']) != len(images_to_process):
                logger.warning(
                    f"Nombre d'images retournées ({len(response['images'])}) "
                    f"ne correspond pas au nombre d'images envoyées ({len(images_to_process)})"
                )
            
            # Traiter les résultats de l'API
            for i, (img_data, img_info) in enumerate(zip(response['images'], images_to_process)):
                if img_data and img_info['output_path']:
                    try:
                        output_path = img_info['output_path']
                        self.decode_and_save_base64(img_data, output_path, overwrite=True)
                        
                        # Mettre à jour le cache
                        if self.use_cache and not skip_cache and self.cache:
                            self.cache.add_to_cache(
                                img_info['path'],
                                output_path,
                                cache_params
                            )
                        
                        # Mettre à jour les résultats à l'index d'origine
                        original_idx = img_info['original_index']
                        results[original_idx] = (output_path, img_info['is_bw'])
                        self._processed_paths.add(str(img_info['path']))
                        logger.info(f"Image {i+1}/{len(images_to_process)} (index original: {original_idx}) sauvegardée avec succès: {output_path}")
                    except Exception as e:
                        original_idx = img_info['original_index']
                        logger.error(f"Erreur lors de la sauvegarde de l'image {output_path} (index original: {original_idx}): {e}")
                        # Garder la valeur par défaut (None, False) pour cette image
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement par lots: {e}")
            logger.error(f"Erreur lors du traitement par lots: {str(e)}")
            logger.info("Tentative de traitement image par image...")
            
            # Fallback: traiter chaque image individuellement
            for img_info in images_to_process:
                try:
                    original_idx = img_info['original_index']
                    logger.info(f"Traitement individuel de l'image {img_info['path']} (index original: {original_idx})")
                    
                    result = self.upscale_image(
                        image_path=img_info['path'],
                        output_path=img_info['output_path'],
                        scale_factor=scale_factor,
                        upscaler=upscaler,
                        denoising_strength=denoising_strength,
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        steps=steps,
                        cfg_scale=cfg_scale,
                        sampler_name=sampler_name,
                        output_format=output_format,
                        auto_colorize=auto_colorize,
                        colorize_prompt=colorize_prompt,
                        colorize_negative_prompt=colorize_negative_prompt
                    )
                    # Mettre à jour les résultats à l'index d'origine
                    results[original_idx] = (result[0], img_info['is_bw'])
                    logger.info(f"Traitement individuel réussi pour l'index {original_idx}: {result[0]}")
                except Exception as single_error:
                    original_idx = img_info['original_index']
                    logger.error(f"Échec du traitement individuel pour l'index {original_idx} ({img_info['path']}): {single_error}", exc_info=True)
                    # Garder la valeur par défaut (None, False) pour cette image
                    continue
            
            return results
    
    def upscale_image(
        self,
        image_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        scale_factor: int = 2,
        upscaler: str = "R-ESRGAN 4x+ Anime6B",
        denoising_strength: float = 0.5,
        prompt: str = "high quality, high resolution, detailed",
        negative_prompt: str = "blurry, lowres, low quality, artifacts, jpeg artifacts",
        steps: int = 20,
        cfg_scale: float = 7.0,
        sampler_name: str = "DPM++ 2M",
        output_format: str = 'PNG',
        auto_colorize: bool = True,
        colorize_prompt: Optional[str] = None,
        colorize_negative_prompt: Optional[str] = None
    ) -> Tuple[Path, bool]:
        """
        Améliore la résolution d'une image avec Stable Diffusion Forge.
        
        Args:
            image_path: Chemin vers l'image source
            output_path: Chemin de sortie pour l'image améliorée (optionnel)
            scale_factor: Facteur d'échelle (1-4)
            upscaler: Nom de l'upscaler à utiliser
            denoising_strength: Force du débruiteur (0-1)
            prompt: Prompt pour guider l'amélioration
            negative_prompt: Éléments à éviter
            steps: Nombre d'étapes de débruiteur
            cfg_scale: Échelle de configuration du classificateur
            sampler_name: Nom de l'échantillonneur à utiliser
            output_format: Format de sortie de l'image
            auto_colorize: Si True, tente de coloriser les images en N&B
            colorize_prompt: Prompt personnalisé pour la colorisation (optionnel)
            colorize_negative_prompt: Prompt négatif pour la colorisation (optionnel)
            
        Returns:
            Tuple contenant le chemin de l'image améliorée et un booléen indiquant si l'image est en N&B
            
        Raises:
            ValueError: Si les paramètres sont invalides
            URLError: Si l'appel à l'API échoue
        """
        logger.debug(f"Début de upscale_image avec image_path={image_path}, output_path={output_path}")
        
        # Validation des entrées
        if not 1 <= scale_factor <= 4:
            error_msg = f"Le facteur d'échelle doit être entre 1 et 4, reçu : {scale_factor}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not 0 <= denoising_strength <= 1:
            error_msg = f"La force du débruiteur doit être entre 0 et 1, reçu : {denoising_strength}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Préparation du chemin de sortie
        output_path = Path(output_path) if output_path else None
        if output_path is None:
            # Alternative à with_stem pour compatibilité avec Python < 3.9
            input_path = Path(image_path)
            # Forcer l'extension .png pour le fichier de sortie
            output_path = input_path.parent / f"{input_path.stem}_upscaled.png"
        else:
            # S'assurer que l'extension est .png
            output_path = Path(output_path).with_suffix('.png')
        
        logger.debug(f"Chemin de sortie défini à : {output_path}")
        
        # Prétraitement de l'image
        try:
            logger.debug("Début du prétraitement de l'image")
            # Prétraiter l'image (conversion de format et redimensionnement)
            processed_img, is_bw = self.preprocess_image(image_path, output_format)
            logger.debug(f"Prétraitement terminé - Taille de l'image : {processed_img.size}, est N&B : {is_bw}")
            
            # Calculer les dimensions cibles en conservant les proportions
            width, height = processed_img.size
            target_width = width * scale_factor
            target_height = height * scale_factor
            
            # Traitement spécial pour les images en noir et blanc
            if is_bw:
                path_str = str(image_path)
                file_name = Path(path_str).name if isinstance(image_path, str) else image_path.name
                
                # Si la colorisation automatique est activée
                if auto_colorize:
                    logger.warning(f"L'image {file_name} semble être en noir et blanc - Tentative de colorisation")
                    try:
                        # Utiliser les prompts personnalisés s'ils sont fournis, sinon utiliser les valeurs par défaut
                        color_prompt = colorize_prompt or "high quality, high resolution, detailed, colorized, vibrant colors"
                        color_negative = colorize_negative_prompt or "black and white, grayscale, blurry, lowres, low quality"
                        
                        logger.debug(f"Colorisation de l'image avec le prompt : {color_prompt}")
                        # Coloriser l'image
                        processed_img = self.colorize_image(
                            image=processed_img,
                            prompt=color_prompt,
                            negative_prompt=color_negative,
                            steps=steps,
                            cfg_scale=cfg_scale,
                            sampler_name=sampler_name
                        )
                        is_bw = False  # L'image n'est plus en N&B après colorisation
                        
                    except Exception as colorize_error:
                        logger.warning(f"Échec de la colorisation de l'image {file_name}: {colorize_error}")
                        # En cas d'échec, continuer avec l'image N&B originale
                        if "black and white" not in prompt.lower() and "monochrome" not in prompt.lower():
                            prompt += ", black and white, monochrome"
                else:
                    logger.info(f"L'image {file_name} est en noir et blanc mais la colorisation automatique est désactivée")
                    # Si la colorisation est désactivée, ajouter des tags N&B au prompt
                    if "black and white" not in prompt.lower() and "monochrome" not in prompt.lower():
                        prompt += ", black and white, monochrome"
            
            # Encoder l'image prétraitée
            encoded_image = self.encode_image_to_base64(processed_img, output_format)
            
        except Exception as e:
            logger.error(f"Erreur lors du prétraitement de l'image {image_path}: {e}")
            logger.exception("Détails de l'erreur de prétraitement :")
            raise
            
        # Préparation de la charge utile pour l'API
        payload = {
            "init_images": [encoded_image],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": sampler_name,
            "scheduler": "Automatic",  # Pour éviter l'avertissement de correction automatique
            "denoising_strength": denoising_strength,
            "width": width,  # Largeur originale
            "height": height,  # Hauteur originale
            "enable_hr": True,
            "hr_scale": scale_factor,
            "hr_upscaler": upscaler,
            "hr_second_pass_steps": int(steps * 0.7),  # 70% des étapes pour la seconde passe
            "resize_mode": 0,  # 0 = Just resize (ne pas forcer le carré)
        }
        
        logger.debug(f"Préparation de la charge utile pour l'API - Taille : {width}x{height}, Scale: {scale_factor}")
        
        # Appel à l'API
        try:
            logger.info(f"Envoi de la requête d'upscaling pour {image_path}")
            
            # Appel à l'API
            response = self._call_api('sdapi/v1/img2img', payload)
            
            # Vérification de la réponse
            if not isinstance(response, dict):
                error_msg = f"Réponse API invalide (type: {type(response)}): {response}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if 'images' not in response or not response['images']:
                logger.error("Aucune image dans la réponse de l'API")
                raise ValueError("Aucune image n'a été retournée par l'API")
            
            # Décodage et sauvegarde de l'image
            try:
                output_path_str = str(output_path)
                logger.info(f"Sauvegarde de l'image upscalée vers {output_path_str}")
                self.decode_and_save_base64(
                    response['images'][0],
                    output_path_str,
                    overwrite=True
                )
                logger.debug("Image sauvegardée avec succès")
                
                # Vérifier que le fichier a été correctement enregistré
                if not output_path.exists() or output_path.stat().st_size == 0:
                    raise ValueError("Le fichier de sortie est vide ou n'a pas été créé")
                    
                logger.info(f"Image sauvegardée avec succès: {output_path}")
                # Retourner le statut N/B en fonction des paramètres
                # Si auto_colorize est False et que l'image était en N/B, on conserve le statut N/B
                # Sinon, on considère que l'image est maintenant en couleur
                if not auto_colorize and is_bw:
                    return output_path, True  # Conserver le statut N/B si auto_colorize est False
                return output_path, False  # Sinon, l'image est considérée comme colorisée
                
            except Exception as save_error:
                logger.error(f"Erreur lors de la sauvegarde de l'image: {save_error}")
                if output_path and output_path.exists():
                    output_path.unlink()  # Supprimer le fichier vide ou corrompu
                raise save_error
            
        except Exception as e:
            logger.error(f"Erreur lors de l'amélioration de l'image {image_path}: {str(e)}", exc_info=True)
            raise
        finally:
            # Nettoyage explicite des ressources
            if 'processed_img' in locals():
                del processed_img
            if 'encoded_image' in locals():
                del encoded_image


def enhance_image(
    image_path: Union[str, Path, List[Union[str, Path]]],
    output_path: Optional[Union[str, Path]] = None,
    api_url: str = "http://127.0.0.1:7860",
    **kwargs: Any
) -> Union[Path, List[Tuple[Path, bool]]]:
    """
    Fonction utilitaire pour améliorer une ou plusieurs images en une seule étape.
    
    Args:
        image_path: Chemin vers l'image source ou liste de chemins
        output_path: Chemin de sortie pour l'image améliorée ou répertoire de sortie
        api_url: URL de l'API Stable Diffusion WebUI
        **kwargs: Arguments supplémentaires à passer à ImageEnhancer.upscale_image() ou upscale_batch()
        
    Returns:
        Pour une seule image: Chemin vers l'image améliorée
        Pour plusieurs images: Liste de tuples (chemin, est_nb) pour chaque image
    """
    enhancer = ImageEnhancer(api_url=api_url)
    
    # Vérifier si c'est un traitement par lots
    if isinstance(image_path, (list, tuple)):
        return enhancer.upscale_batch(
            image_paths=image_path,
            output_dir=output_path if output_path and Path(output_path).is_dir() else None,
            **kwargs
        )
    else:
        # Traitement d'une seule image
        result = enhancer.upscale_image(
            image_path=image_path,
            output_path=output_path,
            **kwargs
        )
        return result[0]  # Retourne uniquement le chemin pour la rétrocompatibilité


def main():
    """Point d'entrée principal pour l'interface en ligne de commande."""
    import argparse
    import sys
    from pathlib import Path
    # Gestion des arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Améliore la qualité des images avec Stable Diffusion Forge')
    parser.add_argument('image_paths', nargs='+', help='Chemin(s) vers l\'image ou les images à améliorer. Peut être un fichier unique, une liste de fichiers, ou un motif glob (ex: \'images/*.jpg\')')
    parser.add_argument('--output', '-o', help='Chemin de sortie (fichier pour une image, répertoire pour plusieurs images, par défaut: <nom_original>_enhanced.<format>)')
    
    # Options de connexion
    parser.add_argument('--api-url', type=str, default='http://127.0.0.1:7860',
                       help='URL de l\'API Stable Diffusion Forge (défaut: http://127.0.0.1:7860)')
    
    # Options de traitement
    parser.add_argument('--scale', type=int, default=2, choices=range(1, 5),
                       help='Facteur d\'échelle (1-4, défaut: 2)')
    parser.add_argument('--upscaler', type=str, default='R-ESRGAN 4x+ Anime6B',
                       help='Nom de l\'upscaler à utiliser (défaut: R-ESRGAN 4x+ Anime6B)')
    parser.add_argument('--denoising-strength', type=float, default=0.5,
                       help='Force du débruiteur (0-1, défaut: 0.5)')
    parser.add_argument('--prompt', type=str, default='high quality, high resolution, detailed',
                       help='Prompt pour guider l\'amélioration')
    parser.add_argument('--negative-prompt', type=str, 
                       default='blurry, lowres, low quality, artifacts, jpeg artifacts',
                       help='Éléments à éviter dans l\'image')
    parser.add_argument('--steps', type=int, default=20, help='Nombre d\'étapes de débruiteur')
    parser.add_argument('--cfg-scale', type=float, default=7.0, 
                       help='Échelle de configuration du classificateur')
    parser.add_argument('--sampler', type=str, default='DPM++ 2M',
                       help='Nom de l\'échantillonneur à utiliser')
    parser.add_argument('--format', type=str, default='PNG', 
                       choices=['PNG', 'JPEG', 'JPG', 'WEBP'],
                       help='Format de sortie (défaut: PNG)')
    
    # Options de colorisation
    parser.add_argument('--no-colorize', action='store_false', dest='auto_colorize',
                       help='Désactive la colorisation automatique des images N/B')
    parser.add_argument('--colorize-prompt', type=str, 
                       help='Prompt personnalisé pour la colorisation')
    parser.add_argument('--colorize-negative-prompt', type=str,
                       help='Prompt négatif personnalisé pour la colorisation')
    
    # Options de cache
    cache_group = parser.add_argument_group('Options de cache')
    cache_group.add_argument('--no-cache', action='store_true',
                           help='Désactive complètement le cache')
    cache_group.add_argument('--force-reprocess', action='store_true',
                           help='Force le retraitement même si l\'image est en cache')
    cache_group.add_argument('--cache-dir', type=str,
                           help='Définit un répertoire personnalisé pour le cache')
    
    # Options générales
    parser.add_argument('--force', action='store_true',
                       help='Force le retraitement même si le fichier de sortie existe déjà')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Active les logs détaillés')
    
    args = parser.parse_args()
    
    try:
        # Développer les motifs glob et résoudre les chemins
        expanded_paths: List[Path] = []
        for pattern in args.image_paths:
            pattern_path = Path(pattern).expanduser()
            
            # Si c'est un répertoire, ajouter tous les fichiers d'images
            if pattern_path.is_dir():
                image_extensions = {'*.jpg', '*.jpeg', '*.png', '*.webp'}
                for ext in image_extensions:
                    expanded_paths.extend(Path(pattern_path).glob('**/' + ext))
                continue
                
            # Si c'est un fichier, l'ajouter directement
            if pattern_path.is_file():
                expanded_paths.append(pattern_path.resolve())
                continue
                
            # Essayer avec glob pour les motifs
            matches = list(Path().glob(pattern))
            if not matches:
                print(f"Avertissement : Aucun fichier ne correspond à '{pattern}'", file=sys.stderr)
                continue
                
            expanded_paths.extend(Path(p).resolve() for p in matches)
        
        if not expanded_paths:
            print("Erreur : Aucun fichier valide à traiter", file=sys.stderr)
            sys.exit(1)
        
        # Créer l'instance de l'améliorateur
        enhancer = ImageEnhancer(api_url=args.api_url)
        
        # Traitement unique ou par lots
        if len(expanded_paths) == 1:
            # Traitement d'une seule image
            output_path, is_bw = enhancer.upscale_image(
                image_path=str(expanded_paths[0]),
                output_path=args.output,
                scale_factor=args.scale,
                auto_colorize=args.auto_colorize
            )
            print(f"Image améliorée enregistrée sous : {output_path}")
            if is_bw and args.auto_colorize:
                print("Note: L'image a été détectée comme noir et blanc et a été colorisée")
        else:
            # Traitement par lots
            output_dir = Path(args.output) if args.output else None
            if output_dir and not output_dir.is_dir():
                print("Erreur : Pour le traitement de plusieurs images, --output doit être un répertoire", 
                      file=sys.stderr)
                sys.exit(1)
            
            # Définir la taille du lot par défaut
            batch_size = getattr(args, 'batch_size', 4)  # Valeur par défaut de 4 si batch_size n'est pas défini
            print(f"Traitement de {len(expanded_paths)} images en lots de {batch_size}...")
            
            # Traiter les images par lots
            for i in range(0, len(expanded_paths), batch_size):
                batch = expanded_paths[i:i + batch_size]
                print(f"\nTraitement du lot {i//batch_size + 1}/{(len(expanded_paths)-1)//batch_size + 1}...")
                
                results = enhancer.upscale_batch(
                    image_paths=[str(p) for p in batch],
                    output_dir=str(output_dir) if output_dir else None,
                    scale_factor=args.scale,
                    auto_colorize=args.auto_colorize
                )
                
                # Afficher les résultats du lot
                for (img_path, (out_path, is_bw)) in zip(batch, results):
                    if out_path:
                        print(f"  ✓ {img_path.name} -> {out_path}" + 
                              (" (colorisée)" if is_bw and args.auto_colorize else ""))
                    else:
                        print(f"  ✗ Échec du traitement de {img_path.name}")
            
            print(f"\nTraitement terminé. {len([r for r in results if r[0]])}/{len(expanded_paths)} images traitées avec succès.")
    
    except KeyboardInterrupt:
        print("\nTraitement interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"Erreur lors du traitement des images : {e}", file=sys.stderr)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Réponse de l'API : {e.response.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
