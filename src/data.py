import pyquoks


# region Providers

class EnvironmentProvider(pyquoks.data.EnvironmentProvider):
    OSU_API_VERSION: str
    OSU_SERVER: str
    OSU_CLIENT_ID: str
    OSU_CLIENT_SECRET: str


# endregion


# region Managers

class ConfigManager(pyquoks.data.ConfigManager):
    class OAuthConfig(pyquoks.data.ConfigManager.Config):
        _SECTION = "OAuth"

        _VALUES = {
            "access_token": str,
            "expires_timestamp": int,
        }

        access_token: str
        expires_timestamp: int

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

    oauth: OAuthConfig
    settings: SettingsConfig


# endregion

# region Services

class LoggerService(pyquoks.data.LoggerService):
    pass

# endregion
