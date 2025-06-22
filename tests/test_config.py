"""Tests pour le module de configuration de Fluxgym-coach."""

import json
import os
from pathlib import Path

from fluxgym_coach.utils.config import Config, get_config


def test_config_singleton():
    """Teste que Config est un singleton."""
    config1 = Config()
    config2 = Config()

    # Vérifier que c'est la même instance
    assert config1 is config2


def test_get_config():
    """Teste la fonction get_config."""
    config1 = get_config()
    config2 = get_config()

    # Vérifier que c'est la même instance
    assert config1 is config2


def test_default_config():
    """Teste que la configuration par défaut est correctement chargée."""
    config = Config()

    # Vérifier quelques valeurs par défaut
    assert config.get("app.version") == "0.1.0"
    assert config.get("app.log_level") == "INFO"
    assert config.get("processing.hash_algorithm") == "sha256"
    assert "jpg" in config.get("processing.supported_extensions")


def test_save_and_load_config(tmp_path: Path):
    """Teste la sauvegarde et le chargement de la configuration."""
    config_file = tmp_path / "test_config.json"

    # Créer une nouvelle configuration et la sauvegarder
    config = Config()
    config.set("app.test_key", "test_value")
    config.save(config_file)

    # Vérifier que le fichier a été créé
    assert config_file.exists()

    # Charger la configuration depuis le fichier
    new_config = Config()
    new_config.load(config_file)

    # Vérifier que la valeur a été chargée correctement
    assert new_config.get("app.test_key") == "test_value"


def test_merge_configs():
    """Teste la fusion des configurations."""
    config = Config()

    # Configuration de base
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    update = {"b": {"d": 4, "e": 5}, "f": 6}

    # Fusionner les configurations
    config._merge_configs(base, update)

    # Vérifier la fusion
    assert base["a"] == 1  # Inchangé
    assert base["b"]["c"] == 2  # Inchangé
    assert base["b"]["d"] == 4  # Mis à jour
    assert base["b"]["e"] == 5  # Ajouté
    assert base["f"] == 6  # Ajouté


def test_get_nonexistent_key():
    """Teste la récupération d'une clé qui n'existe pas."""
    config = Config()

    # Clé qui n'existe pas
    assert config.get("nonexistent.key") is None
    assert config.get("nonexistent.key", "default") == "default"


def test_set_nested_key():
    """Teste la définition d'une clé imbriquée."""
    config = Config()

    # Définir une clé imbriquée
    config.set("a.b.c", 42)

    # Vérifier que la valeur a été définie
    assert config.get("a.b.c") == 42

    # Vérifier que la structure est correcte
    assert isinstance(config.to_dict()["a"], dict)
    assert isinstance(config.to_dict()["a"]["b"], dict)


def test_to_dict():
    """Teste la conversion de la configuration en dictionnaire."""
    config = Config()
    config_dict = config.to_dict()

    # Vérifier que c'est une copie profonde
    assert config_dict is not config._config

    # Vérifier quelques valeurs par défaut
    assert config_dict["app"]["version"] == "0.1.0"
    assert "paths" in config_dict


def test_config_file_creation(tmp_path: Path):
    """Teste la création automatique du fichier de configuration."""
    config_dir = tmp_path / "config"
    config_file = config_dir / "config.json"

    # Le fichier ne doit pas exister au départ
    assert not config_file.exists()

    # Charger la configuration (doit créer le fichier)
    os.environ["FLUXGYM_CONFIG_DIR"] = str(config_dir)
    config = Config()
    config.load()

    # Vérifier que le fichier a été créé
    assert config_file.exists()

    # Vérifier le contenu du fichier
    with open(config_file, "r", encoding="utf-8") as f:
        saved_config = json.load(f)

    assert saved_config["app"]["version"] == "0.1.0"

    # Nettoyer
    del os.environ["FLUXGYM_CONFIG_DIR"]
