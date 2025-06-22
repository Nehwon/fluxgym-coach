"""Tests pour les utilitaires de validation de Fluxgym-coach."""

from pathlib import Path

import pytest

from fluxgym_coach.utils.validators import (
    validate_path,
    validate_string,
    validate_integer,
    validate_float,
    validate_boolean,
    validate_dict,
    validate_list,
    ValidationError,
)


def test_validate_path_existing_file(temp_dir: Path) -> None:
    """Teste la validation d'un chemin de fichier existant."""
    # Créer un fichier temporaire
    test_file = temp_dir / "test_file.txt"
    test_file.touch()

    # Valider le chemin avec l'ancien paramètre
    result = validate_path(test_file, must_exist=True, is_file=True)
    assert result == test_file, "Le chemin du fichier devrait être retourné tel quel"
    
    # Valider avec le nouveau paramètre
    result = validate_path(test_file, must_exist=True, must_be_file=True)
    assert result == test_file, "Le chemin du fichier devrait être retourné tel quel"

    # Vérifier que le fichier existe toujours
    assert test_file.exists(), "Le fichier ne devrait pas être supprimé"


def test_validate_path_nonexistent(tmp_path: Path) -> None:
    """Teste la validation d'un chemin non existant."""
    # Chemin qui n'existe pas
    non_existent = tmp_path / "nonexistent"

    # Doit lever une exception si must_exist=True
    with pytest.raises(ValidationError):
        validate_path(non_existent, must_exist=True)

    # Ne doit pas lever d'exception si must_exist=False (ancienne méthode)
    result = validate_path(non_existent, must_exist=False)
    assert str(result) == str(non_existent.resolve())
    
    # Ne doit pas lever d'exception si must_exist=False (nouvelle méthode)
    result = validate_path(non_existent, must_exist=False, must_be_file=False)
    assert str(result) == str(non_existent.resolve())


def test_validate_path_create_directory(temp_dir: Path) -> None:
    """Teste la création automatique d'un répertoire."""
    new_dir = temp_dir / "new_directory"

    # Valider avec création automatique (ancienne méthode)
    result = validate_path(
        new_dir, must_exist=False, is_file=False, create_if_missing=True
    )
    assert result == new_dir, "Le chemin du répertoire devrait être retourné"
    assert new_dir.is_dir(), "Le répertoire devrait être créé automatiquement"
    
    # Supprimer le répertoire pour le test suivant
    new_dir.rmdir()
    
    # Valider avec création automatique (nouvelle méthode)
    result = validate_path(
        new_dir, must_exist=False, must_be_dir=True, create_if_missing=True
    )
    assert result == new_dir, "Le chemin du répertoire devrait être retourné"
    assert new_dir.is_dir(), "Le répertoire devrait être créé automatiquement"


def test_validate_string():
    """Teste la validation des chaînes de caractères."""
    # Test basique
    assert validate_string("test", "test") == "test"

    # Test de longueur minimale
    with pytest.raises(ValidationError):
        validate_string("a", "test", min_length=2)

    # Test de longueur maximale
    with pytest.raises(ValidationError):
        validate_string("too long", "test", max_length=3)

    # Test de motif regex
    assert validate_string("abc123", "test", pattern=r"^[a-z0-9]+$") == "abc123"
    with pytest.raises(ValidationError):
        validate_string("abc!@#", "test", pattern=r"^[a-z0-9]+$")

    # Test de valeurs autorisées
    assert validate_string("a", "test", allowed_values=["a", "b", "c"]) == "a"
    with pytest.raises(ValidationError):
        validate_string("d", "test", allowed_values=["a", "b", "c"])


def test_validate_integer():
    """Teste la validation des entiers."""
    # Test basique
    assert validate_integer("42", "test") == 42
    assert validate_integer(42, "test") == 42

    # Test de type invalide
    with pytest.raises(ValidationError):
        validate_integer("not a number", "test")

    # Test de valeur minimale
    with pytest.raises(ValidationError):
        validate_integer(5, "test", min_value=10)

    # Test de valeur maximale
    with pytest.raises(ValidationError):
        validate_integer(15, "test", max_value=10)


def test_validate_float():
    """Teste la validation des nombres à virgule flottante."""
    # Test basique
    assert validate_float("3.14", "test") == 3.14
    assert validate_float(3.14, "test") == 3.14

    # Test de type invalide
    with pytest.raises(ValidationError):
        validate_float("not a number", "test")

    # Test de valeur minimale
    with pytest.raises(ValidationError):
        validate_float(2.5, "test", min_value=3.0)

    # Test de valeur maximale
    with pytest.raises(ValidationError):
        validate_float(3.5, "test", max_value=3.0)


def test_validate_boolean():
    """Teste la validation des booléens."""
    # Test des valeurs vraies
    assert validate_boolean(True, "test") is True
    assert validate_boolean("true", "test") is True
    assert validate_boolean("yes", "test") is True
    assert validate_boolean("1", "test") is True

    # Test des valeurs fausses
    assert validate_boolean(False, "test") is False
    assert validate_boolean("false", "test") is False
    assert validate_boolean("no", "test") is False
    assert validate_boolean("0", "test") is False

    # Test de valeur invalide
    with pytest.raises(ValidationError):
        validate_boolean("not a boolean", "test")


def test_validate_dict():
    """Teste la validation des dictionnaires."""
    # Test basique
    test_dict = {"a": 1, "b": 2}
    assert validate_dict(test_dict, "test") == test_dict

    # Test de type invalide
    with pytest.raises(ValidationError):
        validate_dict("not a dict", "test")

    # Test de clés requises
    with pytest.raises(ValidationError):
        validate_dict({"a": 1}, "test", required_keys=["a", "b"])

    # Test de types de valeurs
    assert validate_dict(
        {"a": 1, "b": "test"}, "test", value_types={"a": int, "b": str}
    ) == {"a": 1, "b": "test"}

    with pytest.raises(ValidationError):
        validate_dict({"a": "not an int"}, "test", value_types={"a": int})


def test_validate_dict_invalid() -> None:
    """Teste la validation d'un dictionnaire avec un schéma invalide."""
    error_msg = "La clé 'a' dans test doit être de type int"
    with pytest.raises(ValidationError, match=error_msg):
        validate_dict({"a": "not an int"}, "test", value_types={"a": int})


def test_validate_list():
    """Teste la validation des listes."""
    # Test basique
    test_list = [1, 2, 3]
    assert validate_list(test_list, "test") == test_list

    # Test de type invalide
    with pytest.raises(ValidationError):
        validate_list("not a list", "test")

    # Test de longueur minimale
    with pytest.raises(ValidationError):
        validate_list([1, 2], "test", min_length=3)

    # Test de longueur maximale
    with pytest.raises(ValidationError):
        validate_list([1, 2, 3, 4], "test", max_length=3)

    # Test de type d'éléments
    assert validate_list([1, 2, 3], "test", item_type=int) == [1, 2, 3]

    with pytest.raises(ValidationError):
        validate_list([1, "not an int", 3], "test", item_type=int)
