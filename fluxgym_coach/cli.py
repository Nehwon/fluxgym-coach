"""Interface en ligne de commande pour Fluxgym-coach."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Any

from . import __version__
from .image_cache import ImageCache, get_default_cache
from .description import process_descriptions
from .image_enhancement import ImageEnhancer

# Créer le logger sans configuration pour permettre une configuration ultérieure
logger = logging.getLogger(__name__)


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse les arguments de la ligne de commande.

    Args:
        args: Liste des arguments de la ligne de commande

    Returns:
        Objet contenant les arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Fluxgym-coach: Assistant de préparation de datasets pour Fluxgym"
    )

    # Arguments principaux
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Dossier source contenant les images à traiter",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="datasets",
        help="Dossier de destination pour les datasets traités (défaut: datasets)",
    )
    parser.add_argument(
        "-p",
        "--process",
        type=str,
        choices=["all", "rename", "metadata", "description", "enhance"],
        default="all",
        help="Type de traitement à effectuer (défaut: all)",
    )

    # Options pour le cache
    cache_group = parser.add_argument_group("Options de cache")
    cache_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Désactive complètement l'utilisation du cache",
    )
    cache_group.add_argument(
        "--force-reprocess",
        action="store_true",
        help="Force le retraitement de toutes les images, même si elles sont en cache",
    )
    cache_group.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Dossier personnalisé pour stocker le cache (par défaut: .fluxgym_cache dans le dossier utilisateur)",
    )
    cache_group.add_argument(
        "--clean-cache",
        action="store_true",
        help="Nettoie le cache des entrées obsolètes avant le traitement",
    )

    # Options pour l'amélioration d'image
    enhance_group = parser.add_argument_group("Options d'amélioration d'image")
    enhance_group.add_argument(
        "--api-url",
        type=str,
        default="http://127.0.0.1:7860",
        help="URL de l'API Stable Diffusion Forge (défaut: http://127.0.0.1:7860)",
    )
    enhance_group.add_argument(
        "--scale-factor",
        type=int,
        default=2,
        choices=range(1, 5),
        help="Facteur d'échelle pour l'amélioration d'image (1-4, défaut: 2)",
    )
    enhance_group.add_argument(
        "--denoising-strength",
        type=float,
        default=0.5,
        help="Force du débruiteur (0-1, défaut: 0.5)",
    )
    enhance_group.add_argument(
        "--upscaler",
        type=str,
        default="R-ESRGAN 4x+ Anime6B",
        help="Nom de l'upscaler à utiliser (défaut: R-ESRGAN 4x+ Anime6B)",
    )
    enhance_group.add_argument(
        "--prompt",
        type=str,
        default="high quality, high resolution, detailed",
        help="Prompt pour guider l'amélioration d'image",
    )
    enhance_group.add_argument(
        "--negative-prompt",
        type=str,
        default="blurry, lowres, low quality, artifacts, jpeg artifacts",
        help="Éléments à éviter dans l'image améliorée",
    )

    # Options
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Active les logs détaillés"
    )

    return parser.parse_args(args)


def validate_paths(input_path: str, output_path: str) -> Tuple[Path, Path]:
    """Valide les chemins d'entrée et de sortie.

    Args:
        input_path: Chemin du dossier source
        output_path: Chemin du dossier de destination

    Returns:
        Tuple de (input_path, output_path) validés

    Raises:
        FileNotFoundError: Si le dossier source n'existe pas
        NotADirectoryError: Si le chemin source n'est pas un dossier
    """
    input_dir = Path(input_path).expanduser().absolute()
    output_dir = Path(output_path).expanduser().absolute()

    if not input_dir.exists():
        raise FileNotFoundError(f"Le dossier source n'existe pas: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Le chemin source n'est pas un dossier: {input_dir}")

    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)

    return input_dir, output_dir


def find_image_files(directory: Path) -> List[Path]:
    """Trouve tous les fichiers image dans un répertoire.

    Args:
        directory: Répertoire à scanner

    Returns:
        Liste des chemins d'images trouvés
    """
    extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    image_files: List[Path] = []

    for ext in extensions:
        image_files.extend(directory.glob(f"*{ext}"))
        image_files.extend(directory.glob(f"*{ext.upper()}"))

    return image_files


def setup_cache(args: argparse.Namespace) -> Optional[ImageCache]:
    """Configure et retourne une instance de cache selon les arguments.

    Args:
        args: Arguments de la ligne de commande

    Returns:
        Instance de ImageCache ou None si le cache est désactivé
    """
    if args.no_cache:
        logger.info("Cache désactivé (--no-cache)")
        return None

    cache_dir = args.cache_dir
    if cache_dir:
        cache_dir = Path(cache_dir).expanduser().absolute()
        logger.debug(f"Utilisation du dossier de cache personnalisé: {cache_dir}")

    try:
        cache = get_default_cache(cache_dir=cache_dir)

        if args.clean_cache:
            logger.info("Nettoyage du cache...")
            cache.clean_old_entries()

        if args.force_reprocess:
            logger.info("Mode force-reprocess activé, le cache sera ignoré")

        return cache
    except Exception as e:
        logger.warning(f"Impossible d'initialiser le cache: {e}")
        return None


def main(args: Optional[Sequence[str]] = None) -> int:
    """Point d'entrée principal du programme.

    Args:
        args: Arguments de la ligne de commande (par défaut: sys.argv[1:])

    Returns:
        Code de sortie (0 pour succès, 1 pour erreur)
    """
    # Configurer le logging avec un NullHandler par défaut
    logging.basicConfig(handlers=[logging.NullHandler()])

    try:
        # Convertir les arguments en liste si nécessaire
        if args is None:
            args = sys.argv[1:]
        else:
            args = list(args)  # Conversion sécurisée de Sequence à List

        # Parser les arguments
        parsed_args = parse_args(args)

        # Configurer le niveau de log en fonction du mode verbeux
        log_level = logging.DEBUG if parsed_args.verbose else logging.INFO

        # Réinitialiser les handlers du logger racine
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Configurer le logger avec le niveau approprié
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )

        # S'assurer que notre logger utilise le bon niveau
        logger.setLevel(log_level)

        logger.info(f"Démarrage de Fluxgym-coach v{__version__}")

        # Valider les chemins
        input_dir, output_dir = validate_paths(parsed_args.input, parsed_args.output)
        logger.info(f"Source: {input_dir}")
        logger.info(f"Destination: {output_dir}")
        logger.info(f"Type de traitement: {parsed_args.process}")

        # Configurer le cache
        cache = setup_cache(parsed_args)
        cache_params = {"force_reprocess": parsed_args.force_reprocess}

        # Trouver les fichiers image dans le dossier d'entrée
        image_files = find_image_files(input_dir)
        if not image_files:
            logger.warning("Aucun fichier image trouvé dans le dossier source.")
            return 0

        logger.info(f"{len(image_files)} images trouvées dans le dossier source.")

        # Initialiser la liste des fichiers traités
        processed_files = []

        # Traitement des images (renommage et traitement complet) en premier
        if parsed_args.process in ["all", "rename"]:
            from fluxgym_coach.processor import ImageProcessor

            # Créer une instance de ImageProcessor avec le cache configuré
            processor = ImageProcessor(
                input_dir=input_dir,
                output_dir=output_dir,
                cache=cache,
                cache_params=cache_params if cache else None,
            )

            # Traiter les images et récupérer les chemins des fichiers traités
            logger.debug("Début du traitement des images...")
            for original_path, new_path in processor.process_directory():
                logger.debug(
                    f"Image traitée - Original: {original_path}, Nouveau: {new_path}"
                )
                if new_path:  # Si le traitement a réussi
                    processed_files.append(new_path)  # Conserver l'objet Path

            action = (
                "renommées et traitées" if parsed_args.process == "all" else "renommées"
            )
            logger.info(
                f"Traitement des images terminé. "
                f"{len(processed_files)} images {action} avec succès."
            )
            logger.debug(
                f"Liste des fichiers traités: {[str(p) for p in processed_files]}"
            )

            # Mettre à jour la liste des fichiers pour les étapes suivantes
            image_files = processed_files

        # Traitement des métadonnées après le renommage
        if parsed_args.process in ["all", "metadata"]:
            from fluxgym_coach.metadata import process_metadata

            # Activer les logs de débogage pour le module metadata
            logging.getLogger("fluxgym_coach.metadata").setLevel(logging.DEBUG)
            logger.debug(
                f"=== DÉBUT DU TRAITEMENT DES MÉTADONNÉES (mode: {parsed_args.process}) ==="
            )

            # Déterminer les chemins des fichiers à traiter
            files_to_process = []

            if parsed_args.process == "all" and processed_files:
                # Mode "all" : utiliser les fichiers traités
                logger.debug(
                    f"Mode 'all' - Nombre de fichiers traités: {len(processed_files)}"
                )
                logger.debug(
                    f"Contenu de processed_files: {[str(p) for p in processed_files]}"
                )

                # Les fichiers sont déjà des objets Path, on s'assure juste qu'ils sont absolus
                files_to_process = [p.resolve() for p in processed_files]
                logger.debug(
                    f"Fichiers à traiter (chemins absolus): {[str(p) for p in files_to_process]}"
                )
            else:
                # Mode "metadata" : utiliser les fichiers du répertoire d'entrée
                logger.debug(
                    f"Mode 'metadata' - Recherche des images dans: {input_dir}"
                )
                for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                    files = list(input_dir.glob(ext))
                    logger.debug(f"Fichiers trouvés avec l'extension {ext}: {files}")
                    files_to_process.extend(files)

                # Si aucun fichier n'est trouvé dans l'entrée, vérifier la sortie
                if not files_to_process:
                    logger.debug(
                        f"Aucun fichier trouvé dans {input_dir}, vérification de {output_dir}"
                    )
                    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                        files = list(output_dir.glob(ext))
                        logger.debug(
                            f"Fichiers trouvés dans la sortie avec l'extension {ext}: {files}"
                        )
                        files_to_process.extend(files)

            # Filtrer les fichiers existants
            existing_files = [p for p in files_to_process if p.exists()]

            if not existing_files:
                logger.warning(
                    "Aucun fichier valide trouvé pour le traitement des métadonnées"
                )
            elif len(existing_files) < len(files_to_process):
                missing = len(files_to_process) - len(existing_files)
                logger.warning(
                    f"{missing} fichiers introuvables pour le traitement des métadonnées"
                )

            logger.debug(f"Chemins complets des fichiers à traiter: {existing_files}")

            if existing_files:
                success_count = process_metadata(existing_files, output_dir)
                logger.info(
                    f"Traitement des métadonnées terminé. "
                    f"{success_count}/{len(existing_files)} images traitées avec succès."
                )

                # Vérifier si les fichiers de métadonnées ont été créés
                metadata_dir = output_dir / "metadata"
                if metadata_dir.exists():
                    metadata_files = list(metadata_dir.glob("*.json"))
                    logger.debug(f"Fichiers de métadonnées trouvés: {metadata_files}")
                    for f in metadata_files:
                        logger.debug(f"Taille de {f}: {f.stat().st_size} octets")
            else:
                logger.warning(
                    "Aucun fichier valide trouvé pour le traitement des métadonnées"
                )

        # Génération des descriptions
        if parsed_args.process in ["all", "description"]:
            success_count = process_descriptions(image_files, output_dir)
            logger.info(
                f"Génération des descriptions terminée. "
                f"{success_count}/{len(image_files)} descriptions générées avec succès."
            )

        # Amélioration des images
        if parsed_args.process in ["all", "enhance"]:
            logger.info("Démarrage de l'amélioration des images...")
            enhancer = ImageEnhancer(api_url=parsed_args.api_url)

            # Créer un sous-dossier pour les images améliorées
            enhanced_dir = output_dir / "enhanced"
            enhanced_dir.mkdir(exist_ok=True)

            success_count = 0
            for img_path in image_files:
                try:
                    output_path = enhanced_dir / f"enhanced_{img_path.name}"
                    enhancer.upscale_image(
                        img_path,
                        output_path=output_path,
                        scale_factor=parsed_args.scale_factor,
                        upscaler=parsed_args.upscaler,
                        denoising_strength=parsed_args.denoising_strength,
                        prompt=parsed_args.prompt,
                        negative_prompt=parsed_args.negative_prompt,
                    )
                    success_count += 1
                    logger.debug(f"Image améliorée : {img_path.name} -> {output_path}")
                except Exception as e:
                    logger.error(
                        f"Erreur lors du traitement de {img_path.name}: {str(e)}"
                    )

            logger.info(
                f"Amélioration des images terminée. "
                f"{success_count}/{len(image_files)} images améliorées avec succès."
            )

        logger.info("Traitement terminé avec succès!")
        return 0

    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        if "parsed_args" in locals() and parsed_args.verbose:
            logger.exception("Détails de l'erreur:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
