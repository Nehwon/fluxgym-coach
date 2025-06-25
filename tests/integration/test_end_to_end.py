"""Tests d'intégration de bout en bout pour Fluxgym-coach."""

import shutil
from pathlib import Path
from unittest.mock import patch

from fluxgym_coach.cli import main as cli_main


def test_end_to_end_processing(tmp_path: Path, sample_image: Path):
    """Teste le flux complet de traitement d'images."""
    # Créer une structure de dossiers de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Copier l'image de test plusieurs fois avec des noms différents
    for i in range(3):
        shutil.copy2(sample_image, input_dir / f"test_{i}.jpg")

    # Exécuter la commande CLI en mode verbeux
    with patch(
        "sys.argv",
        ["fluxgym-coach", "--input", str(input_dir), "--output", str(output_dir), "--verbose"],
    ):
        result = cli_main()

    # Vérifier que le traitement s'est bien déroulé
    assert result == 0

    # Vérifier la structure des dossiers de sortie
    assert output_dir.exists()

    # Le dossier de métadonnées doit avoir été créé
    metadata_dir = output_dir / "metadata"
    assert metadata_dir.exists()

    # Vérifier que les fichiers de sortie ont été créés
    output_images = list(output_dir.glob("*.jpg"))
    assert len(output_images) > 0

    # Vérifier que les métadonnées ont été générées
    metadata_files = list(metadata_dir.glob("*.json"))
    assert len(metadata_files) == len(output_images)

    # Vérifier que les noms des fichiers sont des hachages
    for img_path in output_images:
        # Le nom du fichier doit être un hachage de 64 caractères (SHA-256)
        assert len(img_path.stem) == 64

        # Vérifier que le fichier de métadonnées correspondant existe
        metadata_file = metadata_dir / f"{img_path.stem}_metadata.json"
        assert metadata_file.exists()


def test_process_option_metadata_only(tmp_path: Path, sample_image: Path):
    """Teste l'option --process metadata."""
    # Créer une structure de dossiers de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Copier une image de test
    shutil.copy2(sample_image, input_dir / "test.jpg")

    # Exécuter la commande CLI avec --process metadata
    with patch(
        "sys.argv",
        [
            "fluxgym-coach",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--process",
            "metadata",
        ],
    ):
        result = cli_main()

    # Vérifier que le traitement s'est bien déroulé
    assert result == 0

    # Vérifier que seul le dossier de métadonnées a été créé
    assert (output_dir / "metadata").exists()
    assert not any(output_dir.glob("*.jpg"))  # Aucune image ne doit avoir été copiée


def test_verbose_output(tmp_path: Path, sample_image: Path, capsys):
    """Teste la sortie en mode verbeux."""
    # Créer une structure de dossiers de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Copier une image de test
    shutil.copy2(sample_image, input_dir / "test.jpg")

    # Exécuter la commande CLI en mode verbeux
    with patch(
        "sys.argv",
        [
            "fluxgym-coach",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
            "--verbose",
        ],
    ):
        result = cli_main()

    # Vérifier que le traitement s'est bien déroulé
    assert result == 0

    # Capturer la sortie
    captured = capsys.readouterr()

    # Vérifier que des messages de debug sont présents
    assert "DEBUG" in captured.err or "DEBUG" in captured.out
    assert "Traitement terminé" in captured.out or "Traitement terminé" in captured.err
