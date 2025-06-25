"""Module de configuration pour Fluxgym-coach."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, TypeVar, Union
import logging

# Type générique pour la méthode get
T = TypeVar("T")

# Configuration du logging
logger = logging.getLogger(__name__)


def _get_config_dir() -> Path:
    """Retourne le répertoire de configuration.

    Returns:
        Chemin vers le répertoire de configuration
    """
    # Vérifier si une variable d'environnement est définie
    env_config_dir = os.environ.get("FLUXGYM_CONFIG_DIR")
    if env_config_dir:
        return Path(env_config_dir)
    # Sinon, utiliser le répertoire par défaut
    return Path.home() / ".config" / "fluxgym-coach"


def _get_config_file() -> Path:
    """Retourne le chemin du fichier de configuration.

    Returns:
        Chemin vers le fichier de configuration
    """
    config_dir = _get_config_dir()
    return config_dir / "config.json"


# Configuration par défaut
def get_default_config() -> dict:
    """Retourne la configuration par défaut.

    Returns:
        Dictionnaire contenant la configuration par défaut
    """
    return {
        "app": {
            "version": "0.1.0",
            "log_level": "INFO",
            "max_workers": 4,
        },
        "paths": {
            "input_dir": str(Path.home() / "images"),
            "output_dir": str(Path.cwd() / "datasets"),
            "cache_dir": str(_get_config_dir() / "cache"),
        },
        "processing": {
            "hash_algorithm": "sha256",
            "supported_extensions": [
                "jpg",
                "jpeg",
                "png",
                "gif",
                "bmp",
                "tiff",
                "webp",
            ],
            "max_image_size_mb": 50,
        },
        "metadata": {
            "extract_exif": True,
            "extract_iptc": True,
            "extract_xmp": True,
            "save_json": True,
        },
        "ai": {
            "generate_descriptions": False,
            "model_name": "gpt-4-vision-preview",
            "max_tokens": 300,
        },
    }


# Configuration par défaut (maintenue pour la rétrocompatibilité)
DEFAULT_CONFIG = get_default_config()


class Config:
    """Classe de gestion de la configuration de l'application."""

    _instance: Optional["Config"] = None
    _config: Dict[str, Any]
    _initialized: bool

    def __new__(cls) -> "Config":
        """Implémentation du pattern Singleton."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialise la configuration."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._config = {}
        self._initialized = True
        self.load()

    def load(self, config_file: Optional[Path] = None) -> bool:
        """Charge la configuration depuis un fichier.

        Args:
            config_file: Chemin vers le fichier de configuration (optionnel)

        Returns:
            True si le chargement a réussi, False sinon
        """
        config_file = config_file or _get_config_file()

        # Créer le dossier de configuration s'il n'existe pas
        config_dir = _get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)

        # Charger la configuration par défaut
        self._config = self._deep_copy_config(DEFAULT_CONFIG)

        # Si le fichier de configuration existe, le charger
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    if not isinstance(user_config, dict):
                        logger.error(
                            f"Fichier {config_file} ne contient pas "
                            "un objet JSON valide"
                        )
                        return False
                    self._config = self._deep_copy_config(DEFAULT_CONFIG)
                    self._merge_configs(self._config, user_config)
                    logger.info(f"Configuration chargée depuis {config_file}")
                    return True
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de décodage JSON dans {config_file}: {str(e)}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {config_file}: {str(e)}")
            # En cas d'erreur, charger la configuration par défaut
            self._config = self._deep_copy_config(DEFAULT_CONFIG)
            return False

        # Si le fichier n'existe pas, sauvegarder la configuration par défaut
        self._config = self._deep_copy_config(DEFAULT_CONFIG)
        self.save(config_file)
        return True

    def save(self, config_file: Optional[Path] = None) -> bool:
        """Sauvegarde la configuration dans un fichier.

        Args:
            config_file: Chemin vers le fichier de configuration (optionnel)

        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        config_file = config_file or _get_config_file()

        try:
            # Créer le dossier de configuration s'il n'existe pas
            config_dir = config_file.parent
            config_dir.mkdir(parents=True, exist_ok=True)

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

            logger.debug(f"Configuration sauvegardée dans {config_file}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de {config_file}: {str(e)}")
            return False

    def get(self, key: str, default: Optional[T] = None) -> Union[Any, Optional[T]]:
        """Récupère une valeur de configuration.

        Args:
            key: Clé de configuration (peut être une clé imbriquée avec des points,
                 ex: 'app.version')
            default: Valeur par défaut si la clé n'existe pas

        Returns:
            La valeur de configuration ou la valeur par défaut

        Example:
            >>> config = Config()
            >>> version = config.get('app.version', '0.0.0')
        """
        keys = key.split(".")
        value: Any = self._config

        try:
            for k in keys:
                if not isinstance(value, dict) or k not in value:
                    return default
                value = value[k]
            return value
        except (KeyError, TypeError, AttributeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """Définit une valeur de configuration.

        Args:
            key: Clé de configuration (peut être une clé imbriquée avec des points)
            value: Valeur à définir

        Returns:
            True si la mise à jour a réussi, False sinon

        Example:
            >>> config = Config()
            >>> config.set('app.version', '1.0.0')
            True
        """
        keys = key.split(".")
        current: Dict[str, Any] = self._config

        try:
            # Parcourir tous les niveaux sauf le dernier
            for k in keys[:-1]:
                if k not in current or not isinstance(current[k], dict):
                    current[k] = {}
                current = current[k]

            # Définir la valeur finale
            current[keys[-1]] = value
            return True

        except (KeyError, TypeError, AttributeError) as e:
            logger.error(f"Erreur lors de la définition de la clé {key}: {str(e)}")
            return True

    def to_dict(self) -> Dict[str, Any]:
        """Retourne la configuration sous forme de dictionnaire.

        Returns:
            Dictionnaire contenant toute la configuration
        """
        return self._deep_copy_config(self._config)

    def _deep_copy_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une copie profonde d'un dictionnaire de configuration.

        Args:
            config: Configuration à copier (doit être un dictionnaire)

        Returns:
            Nouvelle copie de la configuration

        Example:
            >>> config = Config()
            >>> copy = config._deep_copy_config({'a': 1, 'b': {'c': 2}})
        """
        result: Dict[str, Any] = {}
        for k, v in config.items():
            if isinstance(v, dict):
                result[str(k)] = self._deep_copy_config(v)
            elif isinstance(v, list):
                result[str(k)] = [
                    self._deep_copy_config(item) if isinstance(item, dict) else item
                    for item in v
                ]
            else:
                result[str(k)] = v
        return result

    def _merge_configs(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Fusionne récursivement deux dictionnaires de configuration.

        Args:
            base: Configuration de base à mettre à jour
            update: Nouvelles valeurs de configuration
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                # Ne pas essayer de copier les types non-dictionnaires
                if isinstance(value, dict):
                    base[key] = self._deep_copy_config(value)
                else:
                    base[key] = value


# Instance globale de configuration
config = Config()


def get_config() -> Config:
    """Retourne l'instance de configuration de l'application.

    Returns:
        Instance de la classe Config
    """
    return config
