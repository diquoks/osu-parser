import pyquoks

import src.data


# region data.py

class ConfigManager(src.data.ConfigManager):
    _PATH = pyquoks.utils.get_path("tests/config.ini")

    oauth: src.data.ConfigManager.OAuthConfig
    settings: src.data.ConfigManager.SettingsConfig

# endregion
