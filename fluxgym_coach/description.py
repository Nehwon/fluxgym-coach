"""Module de génération de descriptions pour les images de Fluxgym-coach."""

import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configuration du logging
logger = logging.getLogger(__name__)


def _add_basic_metadata(metadata: Dict[str, Any], parts: List[str]) -> None:
    """Ajoute les métadonnées de base à la description."""
    if "filename" in metadata:
        parts.append(f"Fichier: {metadata['filename']}")

    if "file_size" in metadata:
        parts.append(f"Taille du fichier: {metadata['file_size']} octets")


def _add_datetime_metadata(exif: Dict[str, Any], parts: List[str]) -> None:
    """Ajoute les informations de date et heure à la description."""
    if "DateTimeOriginal" in exif:
        try:
            date_obj = datetime.strptime(exif["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
            parts.append(f"Date de prise de vue: {date_obj.strftime('%d/%m/%Y %H:%M')}")
        except (ValueError, TypeError):
            pass


def _add_camera_info(exif: Dict[str, Any], parts: List[str]) -> None:
    """Ajoute les informations sur l'appareil photo."""
    camera_parts = []
    if "Make" in exif:
        camera_parts.append(exif["Make"])
    if "Model" in exif:
        camera_parts.append(exif["Model"])
    if camera_parts:
        parts.append(f"Appareil: {' '.join(camera_parts)}")


def _add_shooting_parameters(exif: Dict[str, Any], parts: List[str]) -> None:
    """Ajoute les paramètres de prise de vue à la description."""
    # Ouverture
    if "FNumber" in exif:
        parts.append(f"Ouverture: f/{exif['FNumber']}")

    # Vitesse d'obturation
    if "ExposureTime" in exif:
        exposure = exif["ExposureTime"]
        if isinstance(exposure, (int, float)):
            if exposure < 1:
                exposure = f"1/{int(1/exposure)}"
            exposure = f"{exposure}s"
        elif (
            isinstance(exposure, str) and "/" in exposure and not exposure.endswith("s")
        ):
            exposure = f"{exposure}s"
        parts.append(f"Vitesse d'obturation: {exposure}")

    # Focale
    if "FocalLength" in exif:
        focal = exif["FocalLength"]
        if isinstance(focal, str) and "mm" in focal:
            focal = focal.replace(" ", "").replace("mm", "") + "mm"
            parts.append(f"Focale: {focal}")

    # ISO
    if "ISOSpeedRatings" in exif:
        parts.append(f"ISO: {exif['ISOSpeedRatings']}")


def generate_description(metadata: Dict[str, Any]) -> str:
    """Génère une description textuelle à partir des métadonnées d'une image.

    Args:
        metadata: Dictionnaire des métadonnées de l'image

    Returns:
        Description textuelle de l'image
    """
    description_parts: List[str] = []

    # Ajouter les métadonnées de base
    _add_basic_metadata(metadata, description_parts)

    # Traiter les métadonnées EXIF si présentes
    if "exif" in metadata and isinstance(metadata["exif"], dict):
        exif = metadata["exif"]
        _add_datetime_metadata(exif, description_parts)
        _add_camera_info(exif, description_parts)
        _add_shooting_parameters(exif, description_parts)

    # Retourner la description complète
    if not description_parts:
        return "Aucune métadonnée disponible pour cette image."
    return "\n".join(description_parts)


def save_description(description: str, output_path: Path) -> bool:
    """Sauvegarde la description dans un fichier.

    Args:
        description: Texte de la description à sauvegarder
        output_path: Chemin de sortie pour le fichier de description

    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(description)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la description: {str(e)}")
        return False


def process_descriptions(image_paths: List[Path], output_dir: Path) -> int:
    """Traite une liste d'images pour générer des descriptions.

    Args:
        image_paths: Liste des chemins d'images à traiter
        output_dir: Dossier de sortie pour les descriptions

    Returns:
        Nombre de descriptions générées avec succès
    """
    from .metadata import MetadataExtractor

    extractor = MetadataExtractor(output_dir)
    success_count = 0

    for image_path in image_paths:
        try:
            # Extraire et sauvegarder les métadonnées
            metadata = extractor.extract_and_save_metadata(image_path)
            if not metadata:
                continue

            # S'assurer que le nom du fichier est dans les métadonnées
            if "filename" not in metadata:
                metadata["filename"] = image_path.name

            # Générer la description
            description = generate_description(metadata)

            # Créer le nom du fichier de sortie
            output_path = output_dir / f"{image_path.stem}_description.txt"

            # Sauvegarder la description
            if save_description(description, output_path):
                success_count += 1
                logger.debug(f"Description générée pour {image_path}")
            else:
                logger.warning(
                    f"Échec de la génération de la description pour {image_path}"
                )

        except Exception as e:
            logger.error(f"Erreur lors du traitement de {image_path}: {str(e)}")

    return success_count
