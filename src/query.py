from __future__ import annotations
import logging
import data


class OAuthClient:
    _FAILURE_KEYS = {
        "error",
        "authentication",
    }

    def __init__(self) -> None:
        self._config = data.ConfigManager()
        self._logger = data.LoggerService(
            filename=__name__,
            file_handling=self._config.settings.file_logging,
            level=logging.DEBUG if self._config.settings.debug else logging.INFO,
        )

    @property
    def _base_url(self) -> str:
        return f"{self._config.oauth.server}/api/v2"

    @property
    def _oauth_url(self) -> str:
        return f"{self._config.oauth.server}/oauth"

    @property
    def _raw_url(self) -> str:
        return f"{self._config.oauth.server}/osu"
