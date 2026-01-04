import pyquoks


# region Managers

class ConfigManager(pyquoks.data.ConfigManager):
    class OAuthConfig(pyquoks.data.ConfigManager.Config):
        _SECTION = "OAuth"

        _VALUES = {
            "api_version": int,
            "client_id": int,
            "client_secret": str,
            "redirect_uri": str,
            "scopes": list,
            "server": str,
        }

        api_version: int
        client_id: int
        client_secret: str
        redirect_uri: str
        scopes: list
        server: str

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
