"""Module de traitement des images pour Fluxgym-coach."""

import hashlib
import logging
from pathlib import Path
from typing import Iterator, Tuple, Optional
from PIL import Image, UnidentifiedImageError

# Configuration du logging
logger = logging.getLogger(__name__)


class ImageProcessor:
    """Classe pour le traitement des images."""

    # Extensions d'images supportées
    SUPPORTED_EXTENSIONS = {"jpeg", "jpg", "png", "gif", "bmp", "tiff", "webp"}

    def __init__(self, input_dir: Path, output_dir: Path):
        """Initialise le processeur d'images.

        Args:
            input_dir: Dossier source contenant les images
            output_dir: Dossier de destination pour les images traitées
        """
        self.input_dir = input_dir
        self.output_dir = output_dir

        # Créer le dossier de sortie s'il n'existe pas
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_image_file(self, file_path: Path) -> bool:
        """Vérifie si un fichier est une image valide.

        Args:
            file_path: Chemin vers le fichier à vérifier

        Returns:
            bool: True si le fichier est une image valide, False sinon
        """
        if not file_path.is_file():
            return False

        # Vérification de l'extension
        if file_path.suffix[1:].lower() not in self.SUPPORTED_EXTENSIONS:
            return False

        # Vérification du type d'image avec PIL
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except (IOError, OSError, UnidentifiedImageError):
            return False

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

    def get_new_filename(self, file_path: Path, hash_value: str) -> Path:
        """Génère un nouveau nom de fichier basé sur le hachage.

        Args:
            file_path: Chemin du fichier d'origine
            hash_value: Valeur de hachage du fichier

        Returns:
            Nouveau chemin de fichier avec le hachage comme nom
        """
        # Conserver l'extension d'origine
        ext = file_path.suffix.lower()
        new_filename = f"{hash_value}{ext}"
        return self.output_dir / new_filename

    def process_image(self, file_path: Path) -> Optional[Tuple[Path, Path]]:
        """Traite une image unique.

        Args:
            file_path: Chemin du fichier image à traiter

        Returns:
            Tuple[Path, Path] | None: Un tuple (chemin_original, nouveau_chemin) si le
            traitement a réussi, None sinon
        """
        if not self.is_image_file(file_path):
            logger.warning(f"Le fichier n'est pas une image supportée: {file_path}")
            return None

        try:
            # Générer un hachage pour le fichier
            file_hash = self.generate_file_hash(file_path)

            # Créer un nouveau nom de fichier basé sur le hachage
            new_path = self.get_new_filename(file_path, file_hash)

            # Vérifier si le fichier existe déjà dans la destination
            if new_path.exists():
                logger.debug(f"Le fichier existe déjà: {new_path}")
                return (file_path, new_path)

            # Copier le fichier vers le nouveau chemin
            import shutil

            shutil.copy2(file_path, new_path)
            logger.info(f"Image traitée: {file_path.name} -> {new_path.name}")

            return (file_path, new_path)

        except Exception as e:
            logger.error(f"Erreur lors du traitement de {file_path}: {str(e)}")
            return None

    def process_directory(self) -> Iterator[Tuple[Path, Optional[Path]]]:
        """Traite tous les fichiers images d'un répertoire.

        Yields:
            Tuples (chemin_original, nouveau_chemin) pour chaque image traitée
        """
        logger.info(f"Traitement du répertoire: {self.input_dir}")

        # Parcourir récursivement le dossier source
        for file_path in self.input_dir.rglob("*"):
            if file_path.is_file():
                result = self.process_image(file_path)
                if result:
                    yield result


def process_images(input_dir: Path, output_dir: Path) -> int:
    """Fonction principale pour traiter les images.

    Args:
        input_dir: Dossier source contenant les images
        output_dir: Dossier de destination pour les images traitées

    Returns:
        Nombre d'images traitées avec succès
    """
    processor = ImageProcessor(input_dir, output_dir)
    processed_count = 0

    for original, processed in processor.process_directory():
        if processed is not None:
            processed_count += 1

    logger.info(f"Traitement terminé. {processed_count} images traitées avec succès.")
    return processed_count
