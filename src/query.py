import http

import requests

from . import data
from . import models


class OAuthClient:
    _FAILURE_KEYS = {
        "error",
        "authentication",
    }

    def __init__(
            self,
            environment_provider: data.EnvironmentProvider,
            config_manager: data.ConfigManager,
            logger_service: data.LoggerService,
    ) -> None:
        self._environment = environment_provider
        self._config = config_manager
        self._logger = logger_service

    @property
    def _api_url(self) -> str:
        return f"https://{self._environment.OSU_SERVER}/api/v2"

    @property
    def _oauth_url(self) -> str:
        return f"https://{self._environment.OSU_SERVER}/oauth"

    @property
    def _raw_url(self) -> str:
        return f"https://{self._environment.OSU_SERVER}/osu"

    @property
    def _headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            # TODO: "Authorization": f"",
            "x-api-version": str(self._environment.OSU_API_VERSION),
        }

    def _query_helper(
            self,
            request: requests.Request,
            refresh_tokens: bool = True,
            check_failure_keys: bool = True,
    ) -> requests.Response | None:
        if refresh_tokens:
            raise NotImplementedError()

        try:
            response = requests.session().send(request.prepare())
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True
            )
        else:
            if check_failure_keys and not self._FAILURE_KEYS.isdisjoint(response.json().keys()):
                self._logger.log_error(
                    exception=requests.exceptions.RequestException(
                        request=request,
                        response=response,
                    ),
                    raise_again=True,
                )

            return response

    def get_raw_beatmap(self, beatmap_id: int) -> models.RawBeatmap | None:
        """
        Endpoint to retrieve ``.osu`` difficulty files
        :param beatmap_id: ID of the beatmap
        """

        self._logger.info(f"{self.get_raw_beatmap.__name__}({beatmap_id=})")

        response = self._query_helper(
            request=requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._raw_url}/{beatmap_id}",
            ),
            refresh_tokens=False,
            check_failure_keys=False,
        )

        return models.RawBeatmap(
            id=beatmap_id,
            raw=response.content,
        )

    def get_auth_url(self) -> str:
        """
        To obtain an access token, you must first get an authorization code that is created when a user grants permissions to your application

        To request permission from the user, they should be redirected to retrieved link

        osu! documentation: https://osu.ppy.sh/docs/#authorization-code-grant
        :return: URL for authorization
        """

        self._logger.info(f"{self.get_auth_url.__name__}()")

        response = self._query_helper(
            request=requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._oauth_url}/authorize",
                params={
                    "client_id": self._environment.OSU_CLIENT_ID,
                    "redirect_uri": self._environment.OSU_REDIRECT_URI,
                    "response_type": "code",
                    "scope": self._environment.OSU_SCOPE,
                },
            ),
            refresh_tokens=False,
            check_failure_keys=False,
        )

        return response.url
