"""Tests pour le module de traitement d'images de Fluxgym-coach."""

import shutil
from pathlib import Path

from fluxgym_coach.processor import ImageProcessor, process_images


# Les fixtures temp_dir et sample_image sont définies dans conftest.py


def test_image_processor_initialization(temp_dir: Path) -> None:
    """Teste l'initialisation de ImageProcessor."""
    # Créer les chemins de test
    input_dir = temp_dir / "input"
    output_dir = temp_dir / "output"

    # Initialiser le processeur
    processor = ImageProcessor(input_dir, output_dir)

    # Vérifier que les attributs sont correctement définis
    assert processor.input_dir == input_dir
    assert processor.output_dir == output_dir

    # Vérifier que le dossier de sortie a été créé
    assert output_dir.exists()
    assert output_dir.is_dir()


def test_is_image_file(sample_image: Path, temp_dir: Path) -> None:
    """Teste la détection des fichiers images."""
    processor = ImageProcessor(temp_dir, temp_dir / "output")

    # Vérifier que le fichier image de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Vérifier qu'un fichier image est détecté comme tel
    assert (
        processor.is_image_file(sample_image) is True
    ), f"Le fichier {sample_image} devrait être détecté comme une image"

    # Vérifier qu'un fichier texte n'est pas détecté comme image
    text_file = temp_dir / "test.txt"
    text_file.write_text("Ceci n'est pas une image")
    assert (
        processor.is_image_file(text_file) is False
    ), "Un fichier texte ne devrait pas être détecté comme une image"


def test_generate_file_hash(sample_image: Path, temp_dir: Path) -> None:
    """Teste la génération de hachage de fichier."""
    processor = ImageProcessor(temp_dir, temp_dir / "output")

    # Vérifier que le fichier de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Générer un hachage pour le fichier image
    hash_value = processor.generate_file_hash(sample_image)

    # Vérifier que le hachage est une chaîne non vide
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0

    # Vérifier que le même fichier génère le même hachage
    assert hash_value == processor.generate_file_hash(sample_image)

    # Créer un fichier différent pour la comparaison
    different_file = temp_dir / "different.txt"
    different_file.write_text("Contenu différent")

    # Vérifier qu'un fichier différent génère un hachage différent
    assert hash_value != processor.generate_file_hash(different_file)


def test_process_image(sample_image: Path, temp_dir: Path) -> None:
    """Teste le traitement d'une seule image."""
    output_dir = temp_dir / "output"
    processor = ImageProcessor(temp_dir, output_dir)

    # Vérifier que le fichier de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Traiter l'image
    result = processor.process_image(sample_image)

    # Vérifier que le résultat est un tuple (chemin_original, nouveau_chemin)
    assert result is not None, "Le résultat du traitement ne devrait pas être None"
    assert len(result) == 2, "Le résultat devrait être un tuple de 2 éléments"
    assert result[0] == sample_image, "Le premier élément devrait être le chemin source"
    assert (
        result[1].parent == output_dir
    ), "Le fichier de sortie devrait être dans le dossier de sortie"
    assert result[1].exists(), "Le fichier de sortie devrait exister"

    # Vérifier que le fichier de sortie est une image valide
    assert processor.is_image_file(
        result[1]
    ), "Le fichier de sortie devrait être une image valide"

    # Vérifier que le hachage du fichier source et de la destination est le même
    src_hash = processor.generate_file_hash(sample_image)
    dst_hash = processor.generate_file_hash(result[1])
    assert (
        src_hash == dst_hash
    ), "Le hachage des fichiers source et destination devrait être identique"


def test_process_image_duplicate(sample_image: Path, temp_dir: Path) -> None:
    """Teste le traitement d'une image en double."""
    output_dir = temp_dir / "output"
    processor = ImageProcessor(temp_dir, output_dir)

    # Vérifier que le fichier de test existe
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"

    # Traiter l'image une première fois
    result1 = processor.process_image(sample_image)
    assert result1 is not None, "Le premier traitement a échoué"

    # Traiter la même image une deuxième fois (devrait être détectée comme doublon)
    result2 = processor.process_image(sample_image)

    # Vérifier que le résultat est le même que la première fois
    assert result2 is not None, "Le deuxième traitement a échoué"
    assert result2[0] == result1[0], "La source devrait être la même"
    assert (
        result2[1] == result1[1]
    ), "La destination devrait être la même (fichier en double)"


def test_process_directory(sample_image: Path, temp_dir: Path) -> None:
    """Teste le traitement d'un répertoire d'images."""
    # Créer une structure de dossiers de test
    input_dir = temp_dir / "input_images"
    input_dir.mkdir(exist_ok=True)

    # Copier l'image de test plusieurs fois avec des noms différents
    for i in range(3):
        shutil.copy2(sample_image, input_dir / f"image_{i}.jpg")

    output_dir = temp_dir / "output_images"

    # Traiter le répertoire
    processor = ImageProcessor(input_dir, output_dir)
    results = list(processor.process_directory())

    # Vérifier que toutes les images ont été traitées
    assert len(results) == 3, "Toutes les images n'ont pas été traitées"

    # Vérifier que tous les fichiers de sortie existent
    for original_path, new_path in results:
        assert original_path is not None, "Le chemin source ne devrait pas être None"
        assert new_path is not None, "Le chemin de destination ne devrait pas être None"
        assert new_path.exists(), f"Le fichier de sortie {new_path} n'existe pas"
        assert new_path.parent == output_dir, f"Le fichier de sortie {new_path} n'est pas dans le bon répertoire"


def test_process_images_function(sample_image: Path, temp_dir: Path) -> None:
    """Teste la fonction process_images."""
    # Créer une structure de dossiers de test
    input_dir = temp_dir / "input"
    input_dir.mkdir(exist_ok=True)

    # Vérifier que le fichier de test existe et est valide
    assert sample_image is not None, "Le chemin de l'image de test est None"
    assert sample_image.exists(), f"Le fichier de test {sample_image} n'existe pas"
    assert sample_image.is_file(), f"Le chemin {sample_image} n'est pas un fichier valide"

    # Créer des images de test avec un contenu différent pour chaque fichier
    from PIL import Image, ImageDraw

    # Première image (copie de l'image de test existante)
    shutil.copy2(sample_image, input_dir / "img_0.jpg")

    # Deuxième image (création d'une nouvelle image avec un contenu différent)
    img1 = Image.new("RGB", (100, 100), color="blue")
    draw = ImageDraw.Draw(img1)
    draw.text((10, 10), "Image 2", fill="white")
    img1.save(input_dir / "img_1.jpg")

    # Créer un sous-dossier avec une autre image différente
    subdir = input_dir / "subdir"
    subdir.mkdir(exist_ok=True)

    img2 = Image.new("RGB", (100, 100), color="green")
    draw = ImageDraw.Draw(img2)
    draw.text((10, 10), "Image 3", fill="white")
    img2.save(subdir / "sub_img.jpg")

    # Traiter les images
    output_dir = temp_dir / "output"
    count = process_images(input_dir, output_dir)

    # Vérifier que toutes les images ont été traitées
    assert count == 3, (
        "Devrait traiter 3 images au total "
        "(2 dans le dossier racine + 1 dans le sous-dossier)"
    )

    # Vérifier que le bon nombre de fichiers a été créé
    output_files = list(output_dir.glob("**/*.jpg"))
    assert (
        len(output_files) == 3
    ), f"Devrait y avoir 3 fichiers en sortie, trouvé {len(output_files)}"

    # Vérifier que les fichiers de sortie existent et sont des images valides
    for file_path in output_files:
        assert file_path.exists(), f"Le fichier {file_path} n'existe pas"
        assert file_path.stat().st_size > 0, f"Le fichier {file_path} est vide"

        # Vérifier que le nom du fichier est un hachage (64 caractères hexadécimaux)
        import re

        filename = file_path.name
        assert re.match(
            r"^[0-9a-f]{64}\.jpg$", filename
        ), f"Le nom de fichier {filename} n'est pas un hachage valide"
