"""Module d'extraction de métadonnées pour Fluxgym-coach."""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import exifread
from PIL import Image, ExifTags

# Configuration du logging
logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Classe pour l'extraction des métadonnées des images."""

    def __init__(self, output_dir: Path):
        """Initialise l'extracteur de métadonnées.

        Args:
            output_dir: Dossier de sortie pour les métadonnées
        """
        self.output_dir = output_dir
        self.metadata_dir = output_dir / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def generate_file_hash(
        self, file_path: Path, hash_algorithm: str = "sha256"
    ) -> str:
        """Génère un hachage pour un fichier.

        Args:
            file_path: Chemin du fichier à hacher
            hash_algorithm: Algorithme de hachage à utiliser (par défaut: sha256)

        Returns:
            Chaîne de caractères représentant le hachage du fichier
        """
        hasher = hashlib.new(hash_algorithm)

        with open(file_path, "rb") as f:
            # Lire le fichier par blocs pour gérer les gros fichiers
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    def extract_exif_data(self, image_path: Path) -> Dict[str, Any]:
        """Extrait les données EXIF d'une image.

        Args:
            image_path: Chemin de l'image

        Returns:
            Dictionnaire des métadonnées EXIF
        """
        metadata = {}

        try:
            # Utiliser exifread pour extraire les métadonnées brutes
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)

                for tag, value in tags.items():
                    if tag not in (
                        "JPEGThumbnail",
                        "TIFFThumbnail",
                        "Filename",
                        "EXIF MakerNote",
                    ):
                        # Nettoyer la valeur pour la sérialisation JSON
                        try:
                            metadata[str(tag)] = str(value)
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            logger.warning(f"Erreur d'encodage pour le tag {tag}")

        except Exception as e:
            logger.error(
                f"Erreur lors de l'extraction des métadonnées EXIF de "
                f"{image_path}: {str(e)}"
            )

        return metadata

    def extract_basic_metadata(self, image_path: Path) -> Dict[str, Any]:
        """Extrait les métadonnées de base d'une image.

        Args:
            image_path: Chemin de l'image

        Returns:
            Dictionnaire des métadonnées de base
        """
        metadata = {
            "filename": image_path.name,
            "filepath": str(image_path.absolute()),
            "size_bytes": image_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(
                image_path.stat().st_mtime
            ).isoformat(),
            "created": datetime.fromtimestamp(image_path.stat().st_ctime).isoformat(),
        }

        try:
            with Image.open(image_path) as img:
                metadata.update(
                    {
                        "format": img.format,
                        "mode": img.mode,
                        "width": img.width,
                        "height": img.height,
                    }
                )

                # Extraire les informations EXIF supplémentaires
                if hasattr(img, "_getexif") and img._getexif() is not None:
                    exif_data = {}
                    for tag, value in img._getexif().items():
                        if tag in ExifTags.TAGS:
                            tag_name = ExifTags.TAGS[tag]
                            try:
                                # Essayer de convertir en JSON-sérialisable
                                exif_data[tag_name] = str(value)
                            except (TypeError, ValueError):
                                pass

                    if exif_data:
                        metadata["exif"] = exif_data

        except Exception as e:
            logger.error(
                f"Erreur lors de l'extraction des métadonnées de base "
                f"de {image_path}: {str(e)}"
            )

        return metadata

    def save_metadata(self, image_path: Path, metadata: Dict[str, Any]) -> Path:
        """Sauvegarde les métadonnées dans un fichier JSON.

        Args:
            image_path: Chemin de l'image source
            metadata: Dictionnaire des métadonnées à sauvegarder
                (doit contenir 'content_hash')

        Returns:
            Chemin du fichier de métadonnées créé

        Raises:
            KeyError: Si 'content_hash' n'est pas présent dans les métadonnées
        """
        if "content_hash" not in metadata:
            raise KeyError("Le hachage de contenu est requis dans les métadonnées")

        # Créer un nom de fichier basé sur le hachage du contenu
        metadata_file = self.metadata_dir / f"{metadata['content_hash']}_metadata.json"

        try:
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.debug(f"Métadonnées sauvegardées: {metadata_file}")
            return metadata_file

        except Exception as e:
            logger.error(
                f"Erreur lors de la sauvegarde des métadonnées "
                f"pour {image_path}: {str(e)}"
            )
            raise

    def extract_and_save_metadata(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """Extrait et sauvegarde toutes les métadonnées d'une image.

        Args:
            image_path: Chemin de l'image

        Returns:
            Dictionnaire des métadonnées ou None en cas d'erreur
        """
        try:
            # Vérifier si le fichier est une image valide
            if not image_path.is_file():
                logger.warning(
                    f"Le fichier n'existe pas ou n'est pas un fichier "
                    f"valide: {image_path}"
                )
                return None

            # Extraire les métadonnées de base
            metadata = self.extract_basic_metadata(image_path)

            # Extraire les données EXIF détaillées
            exif_data = self.extract_exif_data(image_path)
            if exif_data:
                metadata["exif_detailed"] = exif_data

            # Générer un hachage du contenu de l'image
            file_hash = self.generate_file_hash(image_path)
            metadata["content_hash"] = file_hash

            # Vérifier si les métadonnées pour ce hachage existent déjà
            metadata_file = self.metadata_dir / f"{file_hash}_metadata.json"
            if not metadata_file.exists():
                # Sauvegarder les métadonnées uniquement si elles n'existent pas déjà
                self.save_metadata(image_path, metadata)
            else:
                logger.debug(
                    f"Les métadonnées pour ce contenu existent déjà: {metadata_file}"
                )

            return metadata

        except Exception as e:
            logger.error(
                f"Erreur lors de l'extraction des métadonnées "
                f"pour {image_path}: {str(e)}"
            )
            return None


def process_metadata(image_paths: List[Path], output_dir: Path) -> int:
    """Traite les métadonnées pour une liste d'images.

    Args:
        image_paths: Liste des chemins d'images à traiter
        output_dir: Dossier de sortie pour les métadonnées

    Returns:
        Nombre d'images traitées avec succès
    """
    extractor = MetadataExtractor(output_dir)
    success_count = 0

    for image_path in image_paths:
        if extractor.extract_and_save_metadata(image_path) is not None:
            success_count += 1

    logger.info(
        f"Traitement des métadonnées terminé. {success_count}/"
        f"{len(image_paths)} images traitées avec succès."
    )
    return success_count
