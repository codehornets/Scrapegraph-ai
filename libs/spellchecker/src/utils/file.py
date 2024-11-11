import platform
from pathlib import Path

from libs.spellchecker.src.config.settings import Settings


def load_hunspell_dictionary(settings: Settings, lang: str):
    base_path = Path(
        settings.hunspell_default_dictionary_paths.get(platform.system(), "")
    )

    # Split the language code
    lang_parts = lang.split("_")
    primary_lang = lang_parts[0]

    # Try different possible paths
    possible_paths = [
        base_path / primary_lang,  # e.g., 'en' for 'en_US'
        base_path / lang,  # e.g., 'en_US'
        base_path,  # root directory
    ]

    for lang_path in possible_paths:
        dic_file = lang_path / f"{lang}.dic"
        aff_file = lang_path / f"{lang}.aff"

        if dic_file.exists() and aff_file.exists():
            return str(dic_file), str(aff_file)

    # If we reach here, no dictionary files were found. Let's provide more debug information.
    for path in possible_paths:
        print(f"  {path}")
        if path.exists():
            print(f"Contents of {path}:")
            for item in path.iterdir():
                print(f"{item}")
        else:
            print("Directory does not exist")

    raise ValueError(
        f"No .dic or .aff files found for language {lang}. Base path: {base_path}"
    )


def load_spylls_dictionary_path(
    settings: Settings, lang: str, unsupported: bool = False
):
    if unsupported:
        #  Load mozilla xpi dictionaries
        base_path = Path(
            settings.spylls_unsupported_dictionary_paths.get(platform.system(), "")
        )
    else:
        #  Load default dictionaries
        base_path = Path(
            settings.hunspell_default_dictionary_paths.get(platform.system(), "")
        )

    lang_parts = lang.split("_")
    primary_lang = lang_parts[0]

    possible_paths = [base_path / primary_lang, base_path / lang, base_path]

    for lang_path in possible_paths:
        dic_file = lang_path / f"{lang}.dic"  # Look for the .dic file first
        if dic_file.exists():
            return str(dic_file.with_suffix(""))  # Remove the .dic extension for spylls

    raise ValueError(f"No .dic file found for language {lang}. Base path: {base_path}")
