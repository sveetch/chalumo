from pathlib import Path

import click


# Available profiles
PROFILE_CHOICES = [
    "html",
    "django"
]

# Shared arguments
COMMON_ARGS = {
    "basepath": {
        "kwargs": {
            "type": click.Path(
                file_okay=True, dir_okay=True, writable=True, resolve_path=False,
                path_type=Path, exists=True,
            ),
            "required": True,
        }
    },
}


# Shared arguments
COMMON_OPTIONS = {
    "profile": {
        "args": ("--profile",),
        "kwargs": {
            "metavar": "STRING",
            "type": click.Choice(PROFILE_CHOICES),
            "help": (
                "Template profile to use to parse and lint sources. "
                "'html' (default) won't do anything special since HTML is the basic "
                "format. 'django' enable Django template processors for a workaround "
                "with template tags."
            ),
            "show_default": True,
            "default": PROFILE_CHOICES[0],
        }
    },
    "require-pragma": {
        "args": ("--require-pragma",),
        "kwargs": {
            "metavar": "STRING",
            "help": (
                "Only the files starting with this exact string will be processed and "
                "others ones will be ignored. For compatibility with 'djLint' "
                "environment you should use \"{# djlint:on #}\"."
            ),
            "show_default": True,
            "default": "",
        }
    },
    "pattern": {
        "args": ("--pattern",),
        "kwargs": {
            "metavar": "STRING",
            "help": (
                "Pattern to use for file discovery in given basepath. When given "
                "basepath is a single file path, the pattern will not be used."
            ),
            "show_default": True,
            "default": "",
        }
    },
}
