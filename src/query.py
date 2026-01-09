import datetime
import http

import requests

import src.constants
import src.data
import src.models


class OAuthClient:
    _FAILURE_KEYS = {
        "error",
        "authentication",
    }

    def __init__(
            self,
            environment_provider: src.data.EnvironmentProvider,
            config_manager: src.data.ConfigManager,
            logger_service: src.data.LoggerService,
    ) -> None:
        self._environment = environment_provider
        self._config = config_manager
        self._logger = logger_service

    @property
    def _api_url(self) -> str:
        return f"{self._environment.OSU_SERVER}/api/v2"

    @property
    def _oauth_url(self) -> str:
        return f"{self._environment.OSU_SERVER}/oauth"

    @property
    def _raw_url(self) -> str:
        return f"{self._environment.OSU_SERVER}/osu"

    def _get_headers(self, authorization: bool = False, api_version: bool = False) -> dict:
        base_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if authorization:
            base_headers |= {
                "Authorization": f"Bearer {self._config.oauth.access_token}",
            }

        if api_version:
            base_headers |= {
                "x-api-version": self._environment.OSU_API_VERSION,
            }

        return base_headers

    def _query_helper(
            self,
            request: requests.Request,
            /,
            *,
            refresh_access_token: bool = True,
            check_failure_keys: bool = True,
            is_authorize_client: bool = False,
    ) -> requests.Response | None:
        is_access_token_expired = int(datetime.datetime.now().timestamp()) >= self._config.oauth.expires_timestamp

        if refresh_access_token and is_access_token_expired and not is_authorize_client:
            self.authorize_client()

        try:
            response = requests.session().send(
                request=request.prepare(),
                timeout=src.constants.REQUEST_TIMEOUT,
            )
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True
            )
        else:
            if check_failure_keys and isinstance(response.json(), dict) and not self._FAILURE_KEYS.isdisjoint(
                    response.json().keys()):
                self._logger.log_error(
                    exception=requests.exceptions.RequestException(
                        request=request,
                        response=response,
                    ),
                    raise_again=True,
                )

            return response

    def get_raw_beatmap(self, beatmap_id: int) -> src.models.BeatmapRaw:
        """
        :param beatmap_id: ID of the beatmap
        :return: Content of ``.osu`` file
        """

        self._logger.info(f"{self.get_raw_beatmap.__name__}({beatmap_id=})")

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._raw_url}/{beatmap_id}",
            ),
            refresh_access_token=False,
            check_failure_keys=False,
        )

        return src.models.BeatmapRaw(
            id=beatmap_id,
            raw=response.content,
        )

    def authorize_client(self) -> None:
        """
        The client credential flow provides a way for developers to get access tokens that do not have associated user permissions

        These tokens are considered as guest users

        osu! documentation:
            https://osu.ppy.sh/docs/#client-credentials-grant
        """

        self._logger.info(f"{self.authorize_client.__name__}()")

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.POST,
                url=f"{self._oauth_url}/token",
                headers=self._get_headers(),
                json={
                    "client_id": self._environment.OSU_CLIENT_ID,
                    "client_secret": self._environment.OSU_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                    "scope": "public",
                },
            ),
            refresh_access_token=False,
            is_authorize_client=True,
        )

        request_timestamp = int(datetime.datetime.now().timestamp())
        token_lifetime = response.json().get("expires_in") - src.constants.REQUEST_TIMEOUT

        self._config.oauth.update(
            access_token=response.json().get("access_token"),
            expires_timestamp=request_timestamp + token_lifetime,
        )

    def get_user(self, user_id: int, ruleset: src.models.Ruleset) -> src.models.UserExtended:
        """
        This endpoint returns the detail of specified user

        osu! documentation:
            https://osu.ppy.sh/docs/#get-user
        :param user_id: ID of the user
        :param ruleset: Ruleset name
        """

        self._logger.info(f"{self.get_user.__name__}({user_id=}, {ruleset=})")

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._api_url}/users/{user_id}/{ruleset.value}",
                headers=self._get_headers(
                    authorization=True,
                    api_version=True,
                ),
            ),
        )

        return src.models.UserExtended(**response.json())

    def get_score(self, score_id: int) -> src.models.Score:
        """
        This endpoint returns the detail of specified score

        osu! documentation:
            https://osu.ppy.sh/docs/#get-apiv2scoresrulesetorscorescore
        :param score_id: ID of the score
        """

        self._logger.info(f"{self.get_score.__name__}({score_id=})")

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._api_url}/scores/{score_id}",
                headers=self._get_headers(
                    authorization=True,
                    api_version=True,
                ),
            ),
        )

        return src.models.Score(**response.json())

    def get_latest_user_score(
            self,
            user_id: int,
            ruleset: src.models.Ruleset,
            include_fails: bool = False,
            legacy_only: bool = False,
    ) -> src.models.Score | None:
        """
        This endpoint returns the latest score of specified user

        osu! documentation:
            https://osu.ppy.sh/docs/#get-user-scores
        :param user_id: ID of the user
        :param ruleset: Ruleset of the scores to be returned
        :param include_fails: Include scores of failed plays
        :param legacy_only: Whether or not to exclude lazer scores
        """

        self._logger.info(
            f"{self.get_latest_user_score.__name__}({user_id=}, {ruleset=}, {include_fails=}, {legacy_only=})",
        )

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._api_url}/users/{user_id}/scores/recent",
                headers=self._get_headers(
                    authorization=True,
                    api_version=True,
                ),
                json={
                    "legacy_only": legacy_only,
                    "include_fails": include_fails,
                    "mode": ruleset.value,
                    "limit": 1,
                },
            ),
        )

        if response.json():
            return src.models.Score(**response.json()[0])
        else:
            return None

    def get_best_user_scores(
            self,
            user_id: int,
            ruleset: src.models.Ruleset,
            legacy_only: bool = False
    ) -> list[src.models.Score]:
        """
        This endpoint returns the best scores of specified user

        osu! documentation:
            https://osu.ppy.sh/docs/#get-user-scores
        :param user_id: ID of the user
        :param ruleset: Ruleset of the scores to be returned
        :param legacy_only: Whether or not to exclude lazer scores
        """

        self._logger.info(f"{self.get_latest_user_score.__name__}({user_id=}, {ruleset=}, {legacy_only=})")

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._api_url}/users/{user_id}/scores/best",
                headers=self._get_headers(
                    authorization=True,
                    api_version=True,
                ),
                json={
                    "legacy_only": legacy_only,
                    "mode": ruleset.value,
                    "limit": 200,
                },
            ),
        )

        return [src.models.Score(**score_data) for score_data in response.json()]

    def get_beatmap(self, beatmap_id: int) -> src.models.Beatmap:
        """
        Gets beatmap data for the specified beatmap ID

        osu! documentation:
            https://osu.ppy.sh/docs/#get-beatmap
        :param beatmap_id: The ID of the beatmap
        """

        self._logger.info(f"{self.get_beatmap.__name__}({beatmap_id=})")

        response = self._query_helper(
            requests.Request(
                method=http.HTTPMethod.GET,
                url=f"{self._api_url}/beatmaps/{beatmap_id}",
                headers=self._get_headers(
                    authorization=True,
                    api_version=True,
                ),
            ),
        )

        return src.models.Beatmap(**response.json())
