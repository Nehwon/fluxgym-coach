"""Tests pour l'interface en ligne de commande de Fluxgym-coach."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fluxgym_coach.cli import parse_args, validate_paths, main


def test_parse_args():
    """Teste l'analyse des arguments de ligne de commande."""
    # Test avec des arguments minimaux
    args = parse_args(["--input", "/chemin/entree", "--output", "/chemin/sortie"])
    assert args.input == "/chemin/entree"
    assert args.output == "/chemin/sortie"
    assert args.process == "all"
    assert args.verbose is False

    # Test avec tous les arguments
    args = parse_args(
        [
            "--input",
            "/autre/entree",
            "--output",
            "/autre/sortie",
            "--process",
            "metadata",
            "--verbose",
        ]
    )
    assert args.input == "/autre/entree"
    assert args.output == "/autre/sortie"
    assert args.process == "metadata"
    assert args.verbose is True


def test_parse_args_missing_required():
    """Teste que les arguments obligatoires sont bien requis."""
    # Test avec l'argument --input manquant
    with pytest.raises(SystemExit):
        parse_args(["--output", "/chemin/sortie"])

    # Test avec l'argument --output manquant (doit utiliser la valeur par défaut)
    args = parse_args(["--input", "/chemin/entree"])
    assert args.output == "datasets"  # Valeur par défaut


def test_validate_paths_existing_directory(tmp_path: Path):
    """Teste la validation des chemins existants."""
    # Créer des répertoires de test
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Valider les chemins
    result_input, result_output = validate_paths(str(input_dir), str(output_dir))

    # Vérifier les résultats
    assert result_input == input_dir.resolve()
    assert result_output == output_dir.resolve()

    # Vérifier que le répertoire de sortie a été créé
    assert output_dir.exists()


def test_validate_paths_nonexistent_input(tmp_path: Path):
    """Teste la validation avec un répertoire d'entrée inexistant."""
    input_dir = tmp_path / "nonexistent"
    output_dir = tmp_path / "output"

    # Doit lever une exception car le répertoire d'entrée n'existe pas
    with pytest.raises(FileNotFoundError):
        validate_paths(str(input_dir), str(output_dir))


def test_validate_paths_file_instead_of_dir(tmp_path: Path):
    """Teste la validation avec un fichier au lieu d'un répertoire."""
    # Créer un fichier au lieu d'un répertoire
    input_file = tmp_path / "test.txt"
    input_file.write_text("test")

    output_dir = tmp_path / "output"

    # Doit lever une exception car l'entrée doit être un répertoire
    with pytest.raises(NotADirectoryError):
        validate_paths(str(input_file), str(output_dir))


@patch("fluxgym_coach.cli.parse_args")
@patch("fluxgym_coach.cli.validate_paths")
@patch("fluxgym_coach.cli.find_image_files")
@patch("fluxgym_coach.processor.process_images")
@patch("fluxgym_coach.metadata.process_metadata")
def test_main_success(
    mock_process_metadata,
    mock_process_images,
    mock_find_image_files,
    mock_validate_paths,
    mock_parse_args,
    tmp_path: Path,
):
    """Teste le flux principal avec succès."""
    # Configurer les mocks
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    # Créer des fichiers image simulés
    image_files = [
        input_dir / "image1.jpg",
        input_dir / "image2.png",
        input_dir / "image3.webp",
    ]
    mock_find_image_files.return_value = image_files

    # Configurer les mocks pour les arguments
    mock_args = MagicMock()
    mock_args.input = str(input_dir)
    mock_args.output = str(output_dir)
    mock_args.process = "all"
    mock_args.verbose = False
    mock_parse_args.return_value = mock_args

    # Configurer les valeurs de retour des mocks
    mock_validate_paths.return_value = (input_dir, output_dir)
    mock_process_images.return_value = 3  # 3 images traitées
    mock_process_metadata.return_value = 3  # 3 métadonnées traitées

    # Exécuter la fonction main
    with patch(
        "sys.argv",
        ["fluxgym-coach", "--input", str(input_dir), "--output", str(output_dir)],
    ):
        result = main()

    # Vérifier le résultat
    assert result == 0
    mock_parse_args.assert_called_once()
    mock_validate_paths.assert_called_once_with(str(input_dir), str(output_dir))
    mock_find_image_files.assert_called_once_with(input_dir)
    mock_process_metadata.assert_called_once_with(image_files, output_dir)
    mock_process_images.assert_called_once_with(input_dir, output_dir)


@patch("fluxgym_coach.cli.parse_args")
@patch("fluxgym_coach.cli.validate_paths")
@patch("fluxgym_coach.processor.process_images")
def test_main_verbose(
    mock_process_images, mock_validate_paths, mock_parse_args, tmp_path: Path
):
    """Teste le mode verbeux."""
    # Configurer les mocks
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    mock_args = MagicMock()
    mock_args.input = str(input_dir)
    mock_args.output = str(output_dir)
    mock_args.process = "all"
    mock_args.verbose = True
    mock_parse_args.return_value = mock_args

    mock_validate_paths.return_value = (input_dir, output_dir)
    mock_process_images.return_value = 2

    # Exécuter la fonction main
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
        result = main()

    # Vérifier le résultat
    assert result == 0
    # Vérifier que le niveau de log a été défini sur DEBUG
    from fluxgym_coach.cli import logger

    assert logger.level == 10  # DEBUG


@patch("fluxgym_coach.cli.parse_args")
@patch("fluxgym_coach.cli.validate_paths")
@patch("fluxgym_coach.cli.find_image_files")
@patch("fluxgym_coach.processor.process_images")
@patch("fluxgym_coach.metadata.process_metadata")
def test_main_processing_error(
    mock_process_metadata,
    mock_process_images,
    mock_find_image_files,
    mock_validate_paths,
    mock_parse_args,
    tmp_path: Path,
):
    """Teste la gestion des erreurs lors du traitement."""
    # Configurer les mocks
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    # Créer des fichiers image simulés
    image_files = [
        input_dir / "image1.jpg",
        input_dir / "image2.png",
        input_dir / "image3.webp",
    ]
    mock_find_image_files.return_value = image_files

    # Configurer les mocks pour les arguments
    mock_args = MagicMock()
    mock_args.input = str(input_dir)
    mock_args.output = str(output_dir)
    mock_args.process = "all"
    mock_args.verbose = False
    mock_parse_args.return_value = mock_args

    # Configurer les mocks pour simuler une erreur lors du traitement des images
    mock_validate_paths.return_value = (input_dir, output_dir)
    mock_process_metadata.side_effect = Exception(
        "Erreur lors du traitement des métadonnées"
    )

    # Exécuter la fonction main
    with patch(
        "sys.argv",
        ["fluxgym-coach", "--input", str(input_dir), "--output", str(output_dir)],
    ):
        result = main()

    # Vérifier que le code de retour est 1 (erreur)
    assert result == 1
    mock_parse_args.assert_called_once()
    mock_validate_paths.assert_called_once_with(str(input_dir), str(output_dir))
    mock_find_image_files.assert_called_once_with(input_dir)
    mock_process_metadata.assert_called_once_with(image_files, output_dir)
    # Ne devrait pas être appelé à cause de l'erreur
    mock_process_images.assert_not_called()


def test_main_as_script():
    """Teste que le module peut être exécuté comme un script."""
    # Vérifie que le point d'entrée principal est correctement configuré
    from fluxgym_coach.cli import main as cli_main

    assert callable(cli_main)
