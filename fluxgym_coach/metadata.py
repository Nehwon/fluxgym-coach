"""Module d'extraction de métadonnées pour Fluxgym-coach."""

import json
import logging
import hashlib
import os
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
        try:
            logger.debug(f"Début de save_metadata pour {image_path}")
            logger.debug(f"Contenu des métadonnées: {metadata.keys()}")
            
            if "content_hash" not in metadata:
                raise KeyError("Le hachage de contenu est requis dans les métadonnées")

            # Utiliser le nom du fichier source (sans extension) pour le nom du fichier de métadonnées
            # Cela garantit que le fichier de métadonnées correspondra au format attendu par le test
            metadata_file = self.metadata_dir / f"{image_path.stem}_metadata.json"
            
            # S'assurer que le dossier de métadonnées existe
            logger.debug(f"Création du dossier de métadonnées: {self.metadata_dir}")
            self.metadata_dir.mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"Tentative de sauvegarde des métadonnées dans: {metadata_file}")
            logger.debug(f"Dossier de métadonnées existe: {self.metadata_dir.exists()}")
            logger.debug(f"Droits d'écriture: {os.access(str(self.metadata_dir), os.W_OK)}")
            logger.debug(f"Le fichier de métadonnées existe déjà: {metadata_file.exists()}")

            # Vérifier si le fichier existe déjà
            if metadata_file.exists():
                logger.debug(f"Le fichier de métadonnées existe déjà, il sera écrasé: {metadata_file}")
            
            # Essayer d'écrire dans un fichier temporaire d'abord
            temp_file = metadata_file.with_suffix('.tmp')
            logger.debug(f"Écriture dans un fichier temporaire: {temp_file}")
            
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Vérifier que le fichier temporaire a été créé
                if not temp_file.exists() or temp_file.stat().st_size == 0:
                    raise IOError("Le fichier temporaire n'a pas été créé correctement")
                
                # Remplacer le fichier existant par le fichier temporaire
                if metadata_file.exists():
                    metadata_file.unlink()
                temp_file.rename(metadata_file)
                
                logger.debug(f"Métadonnées sauvegardées avec succès: {metadata_file}")
                logger.debug(f"Fichier de métadonnées existe: {metadata_file.exists()}")
                
                if metadata_file.exists():
                    logger.debug(f"Taille du fichier: {metadata_file.stat().st_size} octets")
                else:
                    logger.error("Le fichier de métadonnées n'existe pas après la sauvegarde")
                
                return metadata_file
                
            except Exception as e:
                logger.error(f"Erreur lors de l'écriture du fichier temporaire: {str(e)}")
                # Essayer de supprimer le fichier temporaire en cas d'erreur
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception as e2:
                        logger.error(f"Impossible de supprimer le fichier temporaire: {str(e2)}")
                raise

        except Exception as e:
            logger.error(
                f"Erreur lors de la sauvegarde des métadonnées "
                f"pour {image_path}: {str(e)}",
                exc_info=True
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
            logger.debug(f"Traitement du fichier: {image_path}")
            logger.debug(f"Le fichier existe: {image_path.exists()}")
            
            # Vérifier si le fichier est une image valide
            if not image_path.is_file():
                logger.warning(
                    f"Le fichier n'existe pas ou n'est pas un fichier "
                    f"valide: {image_path}"
                )
                return None

            logger.debug("Extraction des métadonnées de base...")
            # Extraire les métadonnées de base
            metadata = self.extract_basic_metadata(image_path)
            logger.debug(f"Métadonnées de base extraites: {bool(metadata)}")

            logger.debug("Extraction des données EXIF...")
            # Extraire les données EXIF détaillées
            exif_data = self.extract_exif_data(image_path)
            if exif_data:
                metadata["exif_detailed"] = exif_data
                logger.debug(f"Données EXIF extraites: {len(exif_data)} éléments")
            else:
                logger.debug("Aucune donnée EXIF trouvée")

            logger.debug("Génération du hachage du fichier...")
            # Générer un hachage du contenu de l'image
            file_hash = self.generate_file_hash(image_path)
            metadata["content_hash"] = file_hash
            logger.debug(f"Hachage généré: {file_hash}")

            # Utiliser le nom du fichier (sans extension) comme base pour le nom du fichier de métadonnées
            # Cela garantit que le fichier de métadonnées correspondra au format attendu par le test
            metadata_file = self.metadata_dir / f"{image_path.stem}_metadata.json"
            logger.debug(f"Chemin du fichier de métadonnées: {metadata_file}")
            logger.debug(f"Le fichier de métadonnées existe déjà: {metadata_file.exists()}")
            
            # Toujours régénérer les métadonnées pour s'assurer qu'elles sont à jour
            logger.debug("Sauvegarde des métadonnées...")
            saved_path = self.save_metadata(image_path, metadata)
            logger.debug(f"Métadonnées sauvegardées dans: {saved_path}")
            logger.debug(f"Le fichier de métadonnées existe maintenant: {saved_path.exists() if saved_path else 'N/A'}")

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
    # S'assurer que le dossier de sortie existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialiser l'extracteur de métadonnées
    extractor = MetadataExtractor(output_dir)
    success_count = 0

    for image_path in image_paths:
        try:
            # Vérifier si le fichier existe
            if not image_path.exists():
                # Si le fichier n'existe pas, vérifier s'il s'agit d'un fichier déjà renommé dans le dossier de sortie
                if output_dir in image_path.parents:
                    # Le fichier est déjà dans le dossier de sortie, on peut le traiter directement
                    pass
                else:
                    # Essayer de trouver le fichier dans le dossier de sortie
                    output_file = output_dir / image_path.name
                    if output_file.exists():
                        image_path = output_file
                    else:
                        logger.warning(f"Fichier introuvable: {image_path}")
                        continue
            
            logger.debug(f"Traitement des métadonnées pour: {image_path}")
            
            # Extraire et sauvegarder les métadonnées
            metadata = extractor.extract_and_save_metadata(image_path)
            if metadata is not None:
                success_count += 1
                logger.debug(f"Métadonnées générées avec succès pour: {image_path}")
            else:
                logger.warning(f"Échec de la génération des métadonnées pour: {image_path}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {image_path}: {str(e)}", exc_info=True)
            continue

    logger.info(
        f"Traitement des métadonnées terminé. {success_count}/"
        f"{len(image_paths)} images traitées avec succès."
    )
    return success_count
