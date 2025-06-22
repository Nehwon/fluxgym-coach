"""Configuration des tests pour Fluxgym-coach."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Generator

import pytest

from fluxgym_coach import __version__


def test_version():
    """Teste que la version est correctement définie."""
    assert __version__ == "0.1.0"


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Crée un répertoire temporaire pour les tests.

    Yields:
        Chemin vers le répertoire temporaire
    """
    temp_dir = tempfile.mkdtemp(prefix="fluxgym_test_")
    yield Path(temp_dir)

    # Nettoyer après le test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def sample_image(temp_dir: Path) -> Path:
    """Crée une image d'exemple pour les tests.

    Args:
        temp_dir: Répertoire temporaire

    Returns:
        Chemin vers l'image de test
    """
    from PIL import Image, ImageDraw

    # Créer une image de test simple
    img_path = temp_dir / "test_image.jpg"
    img = Image.new("RGB", (100, 100), color="red")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Test Image", fill="white")
    img.save(img_path)

    return img_path


@pytest.fixture(scope="function")
def sample_image_with_metadata(temp_dir: Path) -> Path:
    """Crée une image avec des métadonnées EXIF pour les tests.

    Args:
        temp_dir: Répertoire temporaire

    Returns:
        Chemin vers l'image de test avec métadonnées
    """
    from PIL import Image, ImageDraw

    img_path = temp_dir / "test_metadata.jpg"
    img = Image.new("RGB", (200, 200), color="blue")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "Image avec métadonnées", fill="white")

    # Ajouter des métadonnées EXIF de base
    exif_data = (
        b"Exif\x00\x00II*\x00\x08\x00\x00\x00\x01\x00\x0e\x01\x02\x00\x07\x00"
        b"\x00\x00\x1a\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00"
        b"\x00\x00\x00\x00Test\x00"
    )
    img.save(img_path, exif=exif_data)

    return img_path


@pytest.fixture(scope="function")
def test_config(temp_dir: Path) -> Dict[str, Path]:
    """Configure l'environnement de test.

    Args:
        temp_dir: Répertoire temporaire

    Returns:
        Dictionnaire contenant les chemins de configuration
    """
    # Créer une structure de dossiers de test
    input_path = temp_dir / "input"
    output_path = temp_dir / "output"
    input_path.mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)

    # Créer quelques fichiers de test
    for i in range(3):
        (input_path / f"test_{i}.txt").write_text(f"Test file {i}")

    # Retourner un dictionnaire avec les chemins importants
    return {"input_path": input_path, "output_path": output_path, "temp_dir": temp_dir}
