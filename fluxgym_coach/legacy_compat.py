"""
Module de compatibilité pour la migration vers le nouveau processeur batch.
Permet d'utiliser la nouvelle implémentation avec l'ancienne interface.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .batch_processor import BatchProcessor
from .image_enhancement import ImageEnhancer


class LegacyBatchProcessor:
    """
    Wrapper pour maintenir la compatibilité avec l'ancienne interface batch.
    Utilise le nouveau BatchProcessor en interne.
    """
    
    def __init__(self, api_url: str = "http://127.0.0.1:7860"):
        """
        Initialise le processeur avec l'URL de l'API.
        
        Args:
            api_url: URL de l'API Stable Diffusion WebUI
        """
        self.api_url = api_url
        self.batch_processor = BatchProcessor(api_url=api_url)
        self.enhancer = ImageEnhancer(api_url=api_url)
    
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
        output_format: str = "PNG",
        auto_colorize: bool = True,
        colorize_prompt: Optional[str] = None,
        colorize_negative_prompt: Optional[str] = None,
        force_reprocess: bool = False,
        skip_cache: bool = False,
    ) -> List[Tuple[Optional[Path], bool]]:
        """
        Améliore la résolution d'un lot d'images (compatibilité avec l'ancienne interface).
        
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
        """
        # Convertir les chemins en objets Path
        image_paths = [Path(p) for p in image_paths]
        
        # Filtrer les chemins qui n'existent pas
        valid_paths = [p for p in image_paths if p.exists()]
        
        # Traiter les images avec le nouveau processeur
        results = self.batch_processor.process_batch(
            image_paths=valid_paths,
            output_dir=output_dir,
            scale_factor=scale_factor,
            upscaler=upscaler,
            output_format=output_format
        )
        
        # Convertir les résultats au format attendu (chemin, est_nb)
        # Pour les chemins non valides, ajouter (None, False)
        result_map = {}
        for path, (output_path, is_bw) in zip(valid_paths, results):
            result_map[path] = (output_path, is_bw)
        
        # Retourner les résultats dans le même ordre que les entrées
        final_results = []
        for path in image_paths:
            if path in result_map:
                final_results.append(result_map[path])
            else:
                final_results.append((None, False))
        
        return final_results


def get_legacy_processor(api_url: str = "http://127.0.0.1:7860") -> LegacyBatchProcessor:
    """
    Crée et retourne une instance de LegacyBatchProcessor.
    
    Args:
        api_url: URL de l'API Stable Diffusion WebUI
        
    Returns:
        Instance de LegacyBatchProcessor
    """
    return LegacyBatchProcessor(api_url=api_url)
