"""
Module pour le traitement par lots d'images avec Stable Diffusion Forge.
Permet de traiter plusieurs images en une seule requête API.
"""

import base64
import logging
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from PIL import Image

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Classe pour le traitement par lots d'images."""
    
    def __init__(self, api_url: str = "http://127.0.0.1:7860"):
        """
        Initialise le processeur de lots avec l'URL de l'API.
        
        Args:
            api_url: URL de l'API Stable Diffusion WebUI
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = 300  # 5 minutes de timeout
    
    def _call_api(self, endpoint: str, payload: dict, **kwargs) -> dict:
        """
        Effectue un appel à l'API Stable Diffusion Forge.
        
        Args:
            endpoint: Point de terminaison de l'API
            payload: Données à envoyer à l'API
            **kwargs: Arguments supplémentaires pour la requête
            
        Returns:
            Réponse de l'API sous forme de dictionnaire
            
        Raises:
            Exception: En cas d'erreur lors de l'appel API
        """
        import requests
        from requests.exceptions import RequestException
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Erreur lors de l'appel à l'API {url}: {e}")
            raise
    
    def _generate_output_path(
        self,
        image_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        output_format: str = "png"
    ) -> Path:
        """
        Génère un chemin de sortie unique pour une image.
        
        Args:
            image_path: Chemin de l'image source
            output_dir: Répertoire de sortie (optionnel)
            output_format: Format de sortie (par défaut: 'png')
            
        Returns:
            Chemin de sortie généré
        """
        image_path = Path(image_path)
        
        # Si aucun répertoire de sortie n'est spécifié, utiliser le même que l'image source
        if output_dir is None:
            output_dir = image_path.parent
        else:
            output_dir = Path(output_dir)
        
        # Créer le répertoire de sortie s'il n'existe pas
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Générer un nom de fichier unique avec horodatage et identifiant aléatoire
        timestamp = int(time.time() * 1000)  # Horodatage en millisecondes
        random_suffix = random.randint(1000, 9999)  # Identifiant aléatoire à 4 chiffres
        
        # Créer le nouveau nom de fichier
        base_name = image_path.stem
        suffix = image_path.suffix or f".{output_format.lower()}"
        output_filename = f"{base_name}_enhanced_{timestamp}_{random_suffix}{suffix}"
        
        return output_dir / output_filename
    
    def _save_image(self, image_data: str, output_path: Union[str, Path]) -> None:
        """
        Enregistre une image encodée en base64 sur le disque.
        
        Args:
            image_data: Données de l'image encodée en base64
            output_path: Chemin de sortie pour l'image
            
        Raises:
            ValueError: Si les données d'image sont invalides
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Supprimer l'en-tête data:image/... s'il est présent
            if "," in image_data:
                image_data = image_data.split(",", 1)[1]
                
            # Décoder et sauvegarder l'image
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_data))
                
            logger.debug(f"Image sauvegardée avec succès: {output_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'image {output_path}: {e}")
            raise
    
    def process_batch(
        self,
        image_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        scale_factor: int = 2,
        upscaler: str = "R-ESRGAN 4x+ Anime6B",
        output_format: str = "PNG",
    ) -> List[Tuple[Path, bool]]:
        """
        Traite un lot d'images en une seule requête API.
        
        Args:
            image_paths: Liste des chemins d'images à traiter
            output_dir: Répertoire de sortie (optionnel)
            scale_factor: Facteur d'échelle (1-4)
            upscaler: Nom de l'upscaler à utiliser
            output_format: Format de sortie des images
            
        Returns:
            Liste de tuples (chemin_sortie, est_nb) pour chaque image traitée
        """
        results = []
        images_to_process = []
        
        # Préparer les résultats avec des valeurs par défaut
        for img_path in image_paths:
            img_path = Path(img_path)
            if not img_path.exists():
                logger.warning(f"Le fichier {img_path} n'existe pas, il sera ignoré")
                results.append((None, False))
                continue
                
            # Lire et valider l'image
            try:
                with Image.open(img_path) as img:
                    # Vérifier que c'est bien une image
                    img.verify()  # Vérifie que le fichier est une image valide
                    
                # Si on arrive ici, l'image est valide, on peut la rouvrir pour le traitement
                with Image.open(img_path) as img:
                    # Convertir en RGB pour éviter les problèmes avec les images en niveaux de gris
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # Vérifier si l'image est en N/B
                    is_bw = img.mode != "RGB" or (
                        img.mode == "RGB" and 
                        img.convert("L").convert("RGB") == img.convert("RGB")
                    )
                    
                    # Générer le chemin de sortie uniquement pour les images valides
                    output_path = self._generate_output_path(img_path, output_dir, output_format.lower())
                    
                    # Ajouter le résultat avec l'information N/B
                    results.append((output_path, is_bw))
                    
                    # Encoder l'image en base64
                    buffered = img.tobytes()
                    encoded_image = base64.b64encode(buffered).decode("utf-8")
                    
                    # Ajouter à la liste de traitement
                    images_to_process.append({
                        "original_index": len(results) - 1,
                        "path": img_path,
                        "output_path": output_path,
                        "image": encoded_image,
                        "is_bw": is_bw
                    })
                    
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'image {img_path}: {e}")
                # Ajouter un résultat d'échec pour cette image
                results.append((None, False))
                continue
        
        # Si aucune image à traiter, retourner les résultats
        if not images_to_process:
            return results
        
        # Préparer la charge utile pour l'API
        payload = {
            "resize_mode": 0,  # 0 = Just resize (ne pas forcer le carré)
            "show_extras_results": False,
            "gfpgan_visibility": 0.0,
            "codeformer_visibility": 0.0,
            "codeformer_weight": 0.0,
            "upscaling_resize": float(scale_factor),
            "upscaling_resize_w": 1024,  # Largeur cible
            "upscaling_resize_h": 1024,  # Hauteur cible
            "upscaling_crop": False,  # Ne pas rogner
            "upscaler_1": upscaler,
            "upscaler_2": "None",
            "extras_upscaler_2_visibility": 0.0,
            "upscale_first": False,
            "imageList": [
                {"data": img["image"], "name": f"image_{i}.{output_format.lower()}"}
                for i, img in enumerate(images_to_process)
            ]
        }
        
        # Appeler l'API
        try:
            logger.info(f"Envoi de la requête de traitement par lots pour {len(images_to_process)} images")
            response = self._call_api("sdapi/v1/extra-batch-images", payload)
            
            # Vérifier la réponse
            if not isinstance(response, dict) or "images" not in response:
                raise ValueError("Réponse API invalide ou manquante")
                
            if len(response["images"]) != len(images_to_process):
                logger.warning(
                    f"Nombre d'images retournées ({len(response['images'])}) "
                    f"ne correspond pas au nombre d'images envoyées ({len(images_to_process)})"
                )
            
            # Traiter les résultats
            for i, (img_data, img_info) in enumerate(zip(response["images"], images_to_process)):
                if not img_data:
                    logger.warning(f"Aucune donnée d'image reçue pour l'index {i}")
                    continue
                    
                try:
                    # Sauvegarder l'image
                    self._save_image(img_data, img_info["output_path"])
                    logger.info(f"Image traitée avec succès: {img_info['output_path']}")
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde de l'image {i}: {e}")
                    # Marquer comme échec dans les résultats
                    results[img_info["original_index"]] = (None, False)
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement par lots: {e}")
            # En cas d'erreur, marquer toutes les images comme échouées
            for img_info in images_to_process:
                results[img_info["original_index"]] = (None, False)
        
        return results
