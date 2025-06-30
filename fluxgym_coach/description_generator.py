"""
Module de génération de description d'images utilisant différents modèles BLIP.

Ce module fournit une interface pour générer des descriptions détaillées d'images
en utilisant des modèles de vision par ordinateur de type BLIP. Il gère le chargement
des modèles, le prétraitement des images, la génération de texte et le post-traitement.

Fonctionnalités principales :
- Support de plusieurs modèles BLIP avec différentes capacités
- Génération de descriptions détaillées avec analyse en plusieurs étapes
- Gestion automatique du GPU/CPU
- Optimisation de la mémoire
"""
import logging
from typing import Dict, List, Optional, Tuple, Union

import torch
from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionnaire des modèles disponibles avec leurs métadonnées
# Chaque modèle est configuré avec :
# - name: Identifiant du modèle sur le hub Hugging Face
# - size_mb: Taille approximative en Mo
# - description: Description courte des capacités du modèle
# - features: Liste des fonctionnalités principales
AVAILABLE_MODELS = {
    "blip-base": {
        "name": "Salesforce/blip-image-captioning-base",
        "size_mb": 1.4 * 1024,  # 1.4GB
        "description": "BLIP Base - Léger et rapide, idéal pour un usage général"
    },
    "blip-large": {
        "name": "Salesforce/blip-image-captioning-large",
        "size_mb": 2.5 * 1024,  # 2.5GB
        "description": "BLIP Large - Plus précis, nécessite plus de mémoire"
    },
    "blip2-2.7b": {
        "name": "Salesforce/blip2-opt-2.7b",
        "size_mb": 10.5 * 1024,  # 10.5GB
        "description": "BLIP2 2.7B - Très précis mais gourmand en ressources"
    }
}

class ImageDescriber:
    """
    Classe principale pour la génération de descriptions d'images.
    
    Cette classe gère le cycle de vie complet de la génération de description :
    1. Chargement du modèle et du processeur
    2. Prétraitement de l'image
    3. Génération de la description
    4. Post-traitement et formatage
    
    Args:
        model_name (str): Identifiant du modèle à utiliser (parmi AVAILABLE_MODELS)
        
    Attributes:
        model_name (str): Identifiant du modèle utilisé
        model_info (dict): Métadonnées du modèle
        device (str): Appareil utilisé pour l'inférence ('cuda' ou 'cpu')
        processor: Processeur pour le prétraitement des images
        model: Modèle de génération de description
    """
    
    def __init__(self, model_name: str = "blip-base"):
        """Initialise le générateur de description avec le modèle spécifié."""
        logger.info(f"Initialisation du générateur avec le modèle: {model_name}")
        
        if model_name not in AVAILABLE_MODELS:
            error_msg = f"Modèle non supporté: {model_name}. Choisissez parmi : {list(AVAILABLE_MODELS.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.model_name = model_name
        self.model_info = AVAILABLE_MODELS[model_name]
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None
        
        logger.info(f"Utilisation du périphérique: {self.device}")
        logger.info(f"Chargement du modèle: {self.model_info['name']}")
        
        self._load_model()
    
    def _load_model(self):
        """
        Charge le modèle et le processeur depuis la bibliothèque Hugging Face.
        
        Cette méthode :
        1. Charge le processeur pour le prétraitement des images
        2. Charge le modèle avec une configuration optimisée
        3. Déplace le modèle sur le périphérique approprié (GPU/CPU)
        4. Passe le modèle en mode évaluation
        
        Raises:
            RuntimeError: Si le chargement du modèle échoue
        """
        try:
            # 1. Chargement du processeur
            logger.info(f"Chargement du processeur pour {self.model_info['name']}")
            self.processor = AutoProcessor.from_pretrained(self.model_info["name"])
            
            # 2. Configuration pour économiser de la mémoire
            logger.info(f"Chargement du modèle {self.model_info['name']}")
            torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
            
            # 3. Chargement du modèle avec gestion de la mémoire
            self.model = BlipForConditionalGeneration.from_pretrained(
                self.model_info["name"],
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # 4. Vérification et ajustement du périphérique
            if self.device.startswith("cuda") and not str(self.model.device).startswith("cuda"):
                self.model = self.model.to(self.device)
            
            # 5. Passage en mode évaluation
            self.model.eval()
            logger.info(f"Modèle chargé avec succès sur {self.model.device}")
            
        except Exception as e:
            error_msg = f"Échec du chargement du modèle: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def generate_description(self, image: Image.Image) -> Tuple[str, Dict]:
        """
        Génère une description détaillée de l'image en plusieurs étapes.
        
        Le processus complet comprend :
        1. Vérification des entrées
        2. Prétraitement de l'image
        3. Génération de la description
        4. Post-traitement et formatage
        5. Génération des métadonnées
        
        Args:
            image (PIL.Image): Image à analyser, doit être au format RGB
            
        Returns:
            Tuple[str, Dict]: 
                - str: Description générée
                - Dict: Métadonnées incluant le modèle utilisé et les paramètres
                
        Raises:
            RuntimeError: Si le modèle ou le processeur n'est pas chargé
            ValueError: Si l'image n'est pas valide
        """
        logger.info("Début de la génération de description")
        
        # 1. Vérification des entrées
        if not self.model or not self.processor:
            error_msg = "Le modèle ou le processeur n'est pas chargé correctement"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        if not isinstance(image, Image.Image):
            error_msg = f"L'image doit être un objet PIL.Image, reçu: {type(image)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if image.mode != "RGB":
            logger.warning(f"Conversion de l'image du mode {image.mode} vers RGB")
            image = image.convert("RGB")
        
        try:
            # 2. Configuration de la génération
            generation_kwargs = {
                "max_length": 300,           # Longueur maximale du texte généré
                "num_beams": 5,              # Nombre de beams pour la recherche
                "no_repeat_ngram_size": 2,   # Évite les répétitions de n-grammes
                "early_stopping": True,      # S'arrête quand le modèle est confiant
                "do_sample": True,           # Active l'échantillonnage
                "top_p": 0.95,               # Filtrage par noyau (nucleus)
                "temperature": 0.7,          # Contrôle le hasard des prédictions
            }
            
            logger.info("Prétraitement de l'image...")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            logger.info("Génération de la description...")
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            # Décodage et nettoyage
            logger.info("Post-traitement de la description...")
            description = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0].strip()
            
            # Nettoyage supplémentaire
            description = description.replace("Caption:", "").strip()
            if description and not description[-1] in '.!?':
                description += "."
            
            # 3. Préparation des métadonnées
            metadata = {
                "model": self.model_name,
                "model_id": self.model_info["name"],
                "device": self.device,
                "generation_params": generation_kwargs,
                "image_size": f"{image.width}x{image.height}",
                "image_mode": image.mode,
            }
            
            logger.info("Génération de description terminée avec succès")
            return description, metadata
            
        except Exception as e:
            error_msg = f"Erreur lors de la génération de la description: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

def get_available_models() -> Dict[str, Dict]:
    """
    Retourne les informations sur les modèles disponibles.
    
    Returns:
        Dict[str, Dict]: Dictionnaire des modèles disponibles avec leurs métadonnées
    """
    return AVAILABLE_MODELS.copy()


def get_model_info(model_name: str) -> Dict:
    """
    Récupère les informations d'un modèle spécifique.
    
    Args:
        model_name (str): Identifiant du modèle
        
    Returns:
        Dict: Métadonnées du modèle
        
    Raises:
        ValueError: Si le modèle n'existe pas
    """
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Modèle non trouvé: {model_name}")
    return AVAILABLE_MODELS[model_name]
