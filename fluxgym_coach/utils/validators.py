"""Module de validation pour Fluxgym-coach."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, TypeVar, Type, cast

# Configuration du logging
logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Exception levée lors de la validation des données."""

    pass


def _validate_path_exists(path_obj: Path, must_exist: bool) -> None:
    """Vérifie si le chemin existe si nécessaire."""
    if must_exist and not path_obj.exists():
        raise ValidationError(f"Le chemin n'existe pas: {path_obj}")


def _validate_path_type(path_obj: Path, is_file: bool) -> None:
    """Valide le type de chemin (fichier ou répertoire)."""
    if not path_obj.exists():
        return

    if is_file and not path_obj.is_file():
        raise ValidationError(
            f"Le chemin existe mais n'est pas un fichier: {path_obj}"
        )

    if not is_file and not path_obj.is_dir():
        raise ValidationError(
            f"Le chemin existe mais n'est pas un répertoire: {path_obj}"
        )


def _create_directory_if_needed(path_obj: Path, create_if_missing: bool) -> None:
    """Crée le répertoire si nécessaire."""
    if create_if_missing and not path_obj.exists():
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ValidationError(
                f"Impossible de créer le répertoire {path_obj}: {e}"
            ) from e


T = TypeVar('T', str, Path)

def validate_path(
    path: Union[str, Path, None],
    must_exist: bool = False,
    create_if_missing: bool = False,
    is_file: bool = False,
    must_be_file: Optional[bool] = None,
    must_be_dir: Optional[bool] = None,
) -> Path:
    """Valide un chemin de fichier ou de répertoire.

    Args:
        path: Chemin à valider
        must_exist: Si True, le chemin doit exister
        create_if_missing: Si True, crée le répertoire s'il n'existe pas
        is_file: Si True, le chemin doit être un fichier

    Returns:
        Path: Objet Path validé

    Raises:
        ValidationError: Si la validation échoue
    """
    if path is None:
        raise ValidationError("Le chemin ne peut pas être None")

    # Gestion de la compatibilité avec les anciens paramètres
    if must_be_file is not None:
        is_file = must_be_file
    elif must_be_dir is not None:
        is_file = not must_be_dir
        
    path_obj = Path(str(path)).expanduser().resolve()

    if not must_exist and not create_if_missing:
        _validate_path_type(path_obj, is_file)
        return path_obj

    if must_exist:
        _validate_path_exists(path_obj, must_exist)
        _validate_path_type(path_obj, is_file)
    elif create_if_missing and not is_file:
        _create_directory_if_needed(path_obj, create_if_missing)

    return path_obj


def validate_image_file(
    file_path: Union[str, Path],
    allowed_extensions: Optional[Set[str]] = None,
    max_size_mb: int = 50,
) -> Path:
    """Valide un fichier image.

    Args:
        file_path: Chemin du fichier image
        allowed_extensions: Extensions autorisées (sans point)
        max_size_mb: Taille maximale en Mo

    Returns:
        Objet Path du fichier image validé

    Raises:
        ValidationError: Si la validation échoue
    """
    if allowed_extensions is None:
        allowed_extensions = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"}

    # Valider le chemin de base
    path = validate_path(file_path, must_exist=True, must_be_file=True)

    # Vérifier l'extension
    ext = path.suffix[1:].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Extension de fichier non supportée: {ext}. "
            f"Extensions autorisées: {', '.join(sorted(allowed_extensions))}"
        )

    # Vérifier la taille du fichier
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = path.stat().st_size

    if file_size > max_size_bytes:
        raise ValidationError(
            f"Le fichier est trop volumineux: {file_size / (1024 * 1024):.2f} MB "
            f"(max: {max_size_mb} MB)"
        )

    # Vérifier que c'est bien une image valide
    try:
        from PIL import Image

        with Image.open(path) as img:
            img.verify()
    except Exception as e:
        raise ValidationError(f"Le fichier n'est pas une image valide: {str(e)}")

    return path


def validate_string(
    value: Any,
    name: str = "chaîne",
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    allowed_values: Optional[List[str]] = None,
) -> str:
    """Valide une chaîne de caractères.

    Args:
        value: Valeur à valider
        name: Nom du paramètre pour les messages d'erreur
        min_length: Longueur minimale (inclusive)
        max_length: Longueur maximale (inclusive)
        pattern: Modèle regex pour la validation
        allowed_values: Liste des valeurs autorisées

    Returns:
        La chaîne validée

    Raises:
        ValidationError: Si la validation échoue
    """
    if not isinstance(value, str):
        raise ValidationError(f"La valeur de {name} doit être une chaîne de caractères")

    value = value.strip()
    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"La {name} doit contenir au moins {min_length} caractères"
        )

    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"La {name} ne doit pas dépasser {max_length} caractères")

    if pattern is not None and not re.match(pattern, value):
        raise ValidationError(f"La {name} ne correspond pas au format attendu")

    if allowed_values is not None and value not in allowed_values:
        raise ValidationError(
            f"La {name} doit être l'une des valeurs suivantes: "
            f"{', '.join(allowed_values)}"
        )

    # On s'assure que le type de retour est bien str
    return str(value)


def validate_integer(
    value: Any,
    name: str = "entier",
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> int:
    """Valide un entier.

    Args:
        value: Valeur à valider
        name: Nom du paramètre pour les messages d'erreur
        min_value: Valeur minimale (inclusive)
        max_value: Valeur maximale (inclusive)

    Returns:
        L'entier validé

    Raises:
        ValidationError: Si la validation échoue
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"La valeur de {name} doit être un nombre entier")

    if min_value is not None and int_value < min_value:
        raise ValidationError(
            f"La valeur de {name} doit être supérieure ou égale à {min_value}"
        )

    if max_value is not None and int_value > max_value:
        raise ValidationError(
            f"La valeur de {name} doit être inférieure ou égale à {max_value}"
        )

    return int_value


def validate_float(
    value: Any,
    name: str = "nombre",
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
) -> float:
    """Valide un nombre à virgule flottante.

    Args:
        value: Valeur à valider
        name: Nom du paramètre pour les messages d'erreur
        min_value: Valeur minimale (inclusive)
        max_value: Valeur maximale (inclusive)

    Returns:
        Le float validé

    Raises:
        ValidationError: Si la validation échoue
    """
    try:
        float_value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"La valeur de {name} doit être un nombre")

    if min_value is not None and float_value < min_value:
        raise ValidationError(
            f"La valeur de {name} doit être supérieure ou égale à {min_value}"
        )

    if max_value is not None and float_value > max_value:
        raise ValidationError(
            f"La valeur de {name} doit être inférieure ou égale à {max_value}"
        )

    return float_value


def validate_boolean(value: Any, name: str = "booléen") -> bool:
    """Convertit une valeur en booléen.

    Args:
        value: Valeur à convertir
        name: Nom du paramètre pour les messages d'erreur

    Returns:
        La valeur booléenne

    Raises:
        ValidationError: Si la conversion échoue
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.lower().strip()
        if value in ("true", "t", "yes", "y", "1"):
            return True
        if value in ("false", "f", "no", "n", "0"):
            return False

    try:
        return bool(int(value))
    except (TypeError, ValueError):
        pass

    raise ValidationError(
        f"La valeur de {name} doit être un booléen " "(true/false, oui/non, 1/0)"
    )


def validate_dict(
    value: Any,
    name: str = "dictionnaire",
    required_keys: Optional[List[str]] = None,
    value_types: Optional[Dict[str, type]] = None,
) -> Dict[str, Any]:
    """Valide un dictionnaire.

    Args:
        value: Valeur à valider
        name: Nom du paramètre pour les messages d'erreur
        required_keys: Clés requises dans le dictionnaire
        value_types: Types attendus pour les valeurs (clé -> type)

    Returns:
        Le dictionnaire validé

    Raises:
        ValidationError: Si la validation échoue
    """
    if not isinstance(value, dict):
        raise ValidationError(f"La valeur de {name} doit être un dictionnaire")

    if required_keys:
        missing_keys = [k for k in required_keys if k not in value]
        if missing_keys:
            raise ValidationError(
                f"Clés manquantes dans {name}: {', '.join(missing_keys)}"
            )

    if value_types:
        for key, expected_type in value_types.items():
            if key in value and not isinstance(value[key], expected_type):
                raise ValidationError(
                    f"La clé '{key}' dans {name} doit être de type "
                    f"{expected_type.__name__}"
                )

    return value


def validate_list(
    value: Any,
    name: str = "liste",
    min_length: int = 0,
    max_length: Optional[int] = None,
    item_type: Optional[type] = None,
) -> List[Any]:
    """Valide une liste.

    Args:
        value: Valeur à valider
        name: Nom du paramètre pour les messages d'erreur
        min_length: Longueur minimale (inclusive)
        max_length: Longueur maximale (inclusive)
        item_type: Type attendu pour les éléments de la liste

    Returns:
        La liste validée

    Raises:
        ValidationError: Si la validation échoue
    """
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"La valeur de {name} doit être une liste")

    value_list = list(value)

    if len(value_list) < min_length:
        raise ValidationError(f"La {name} doit contenir au moins {min_length} éléments")

    if max_length is not None and len(value_list) > max_length:
        raise ValidationError(
            f"{name} ne doit pas contenir plus de {max_length} éléments"
        )

    if item_type is not None:
        for i, item in enumerate(value_list, 1):
            if not isinstance(item, item_type):
                raise ValidationError(
                    f"L'élément {i} de {name} doit être de type "
                    f"{item_type.__name__}"
                )

    return value_list
