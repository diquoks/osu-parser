import pyquoks


# region Providers

class EnvironmentProvider(pyquoks.data.EnvironmentProvider):
    OSU_API_VERSION: str
    OSU_SERVER: str
    OSU_CLIENT_ID: str
    OSU_CLIENT_SECRET: str
    OSU_REDIRECT_URI: str
    OSU_SCOPE: str


# endregion


# region Managers

class ConfigManager(pyquoks.data.ConfigManager):
    class SettingsConfig(pyquoks.data.ConfigManager.Config):
        _SECTION = "Settings"

        _VALUES = {
            "debug": bool,
            "file_logging": bool,
            "version": str,
        }

        debug: bool
        file_logging: bool
        version: str

    settings: SettingsConfig


# endregion

# region Services

class LoggerService(pyquoks.data.LoggerService):
    pass

# endregion
