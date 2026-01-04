from . import data


class OAuthClient:
    _FAILURE_KEYS = {
        "error",
        "authentication",
    }

    def __init__(
            self,
            config_manager: data.ConfigManager,
            logger_service: data.LoggerService,
    ) -> None:
        self._config = config_manager
        self._logger = logger_service

    @property
    def _api_url(self) -> str:
        return f"{self._config.oauth.server}/api/v2"

    @property
    def _oauth_url(self) -> str:
        return f"{self._config.oauth.server}/oauth"

    @property
    def _raw_url(self) -> str:
        return f"{self._config.oauth.server}/osu"
