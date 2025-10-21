from __future__ import annotations
import datetime, logging, sys
import requests
import models, data


def check_for_updates(version: str, beta: bool = False) -> bool | None:
    try:
        return not beta and requests.get(
            "https://api.github.com/repos/diquoks/osu-parser/releases/latest",
        ).json()["tag_name"] != version
    except:
        return None


class OAuthClient:
    _ENDPOINT_URL = "https://{0}"
    _FAILURE_KEYS = {"error", "authentication"}
    _DEBUG_STRING = "{0}: {1}"
    client_id: int
    client_secret: str
    redirect_uri: str
    scopes: str
    server: str

    def __init__(self, config: data.ConfigProvider) -> None:
        self._config = config
        for setting, value in self._config.oauth.values.items():
            setattr(self, setting, value)
        self._ENDPOINT_URL = self._ENDPOINT_URL.format(self.server)
        self._BASE_URL = f"{self._ENDPOINT_URL}/api/v2"
        self._OAUTH_URL = f"{self._ENDPOINT_URL}/oauth"
        self._RAW_URL = f"{self._ENDPOINT_URL}/osu"
        self._registry = data.RegistryManager()
        self._logger = data.LoggerService(
            name=__name__,
            file_handling=self._config.settings.file_logging,
            level=logging.DEBUG if self._config.settings.beta else logging.INFO,
        )

    @staticmethod
    def convert_expire_date(json_data: dict) -> dict:
        json_data.update({
            "expires_in": int((datetime.datetime.now() + datetime.timedelta(
                seconds=json_data["expires_in"],
            )).timestamp()),
        })
        return json_data

    @staticmethod
    def extract_expire_date(json_data: dict) -> dict | None:
        json_data.update({"expires_in": datetime.datetime.fromtimestamp(json_data["expires_in"])})
        return json_data

    def _query_helper(
            self,
            request: requests.PreparedRequest = None,
            refresh_access_token: bool = True,
    ) -> requests.Response | None:
        self._registry.refresh()
        self._logger.debug(
            self._DEBUG_STRING.format(sys._getframe().f_code.co_name, "Succeeded self._registry.refresh()"),
        )
        if refresh_access_token and (
                (
                        self._registry.oauth.expires_in and self._registry.oauth.expires_in < datetime.datetime.now().timestamp()
                ) or None in self._registry.oauth.values.values()
        ):
            self._logger.debug(
                self._DEBUG_STRING.format(sys._getframe().f_code.co_name, "Scheduled refresh_access_token()"),
            )
            self.refresh_access_token(refresh_token=self._registry.oauth.refresh_token)
            self._logger.debug(
                self._DEBUG_STRING.format(sys._getframe().f_code.co_name, "Succeeded refresh_access_token()"),
            )
        if request:
            while True:
                try:
                    response = requests.Session().send(request)
                except Exception as e:
                    if isinstance(e, requests.exceptions.ConnectionError):
                        pass
                    else:
                        raise e
                else:
                    return response
        else:
            return None

    def _get_headers(self, include_api_version: bool = False, include_authorization: bool = False) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-version": "20240529" if include_api_version else str(),
            "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}" if include_authorization and None not in (
                self._registry.oauth.token_type, self._registry.oauth.access_token,
            ) else str(),
        }

    def _check_failure_keys(self, request_data: dict) -> bool | None:
        if isinstance(request_data, dict):
            return len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int()
        return None

    def get_raw_beatmap(self, beatmap: int) -> models.RawBeatmapContainer | None:
        """
        Endpoint to retrieve ``.osu`` difficulty files
        :param beatmap: ID of the beatmap
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._RAW_URL}/{beatmap}",
            ).prepare(),
            refresh_access_token=False,
        )
        return models.RawBeatmapContainer({
            "id": beatmap,
            "bytes": request.content,
        }) if request.content else None

    def get_auth_url(self) -> str:
        """
        To obtain an access token, you must first get an authorization code that is created when a user grants permissions to your application

        To request permission from the user, they should be redirected to retrieved link

        osu! documentation: https://osu.ppy.sh/docs/#authorization-code-grant
        :return: URL for authorization
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._OAUTH_URL}/authorize",
                params={
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri,
                    "response_type": "code",
                    "scope": self.scopes,
                },
            ).prepare(),
            refresh_access_token=False,
        )
        return request.url

    def get_access_token(self, code: str) -> bool | None:
        """
        Exchange authorization code for an access token

        osu! documentation: https://osu.ppy.sh/docs/#authorization-code-grant
        :param code: The code you received
        :return: ``True`` if authorization was successful
        """

        request = self._query_helper(
            request=requests.Request(
                method="POST",
                url=f"{self._OAUTH_URL}/token",
                headers=self._get_headers(),
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                },
            ).prepare(),
            refresh_access_token=False,
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            self._registry.oauth.update(**self.convert_expire_date(request_data))
            return True
        else:
            raise Exception(request_data)

    def refresh_access_token(self, refresh_token: str) -> bool | None:
        """
        Refresh the token to get new access token without going through authorization process again

        osu! documentation: https://osu.ppy.sh/docs/#authorization-code-grant
        :param refresh_token: Value of refresh token received from previous access token request
        :return: ``True`` if refreshing was successful
        """

        request = self._query_helper(
            request=requests.Request(
                method="POST",
                url=f"{self._OAUTH_URL}/token",
                headers=self._get_headers(),
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": self.scopes,
                },
            ).prepare(),
            refresh_access_token=False,
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            self._registry.oauth.update(**self.convert_expire_date(request_data))
            return True
        else:
            raise Exception(request_data)

    def revoke_current_token(self) -> bool | None:
        """
        Revokes currently authenticated token

        osu! documentation: https://osu.ppy.sh/docs/#revoke-current-token
        :return: ``True`` if revocation was successful
        """

        request = self._query_helper(
            request=requests.Request(
                method="DELETE",
                url=f"{self._BASE_URL}/oauth/tokens/current",
                headers=self._get_headers(include_authorization=True),
            ).prepare(),
            refresh_access_token=False,
        )
        try:
            request.json()
        except:
            return True
        else:
            raise Exception(request)

    def get_own_data(self, ruleset: str = None) -> models.User | None:
        """
        Similar to ``get_user`` but with authenticated user (token owner) as ``user_id``

        osu! documentation: https://osu.ppy.sh/docs/#get-own-data
        :param ruleset: Ruleset of the scores to be returned
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/me{str() if not ruleset else f"/{ruleset}"}",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.User(request_data)
        else:
            raise Exception(request_data)

    def get_user(self, user: int, ruleset: str = None) -> models.User | None:
        """
        This endpoint returns the detail of specified user

        osu! documentation: https://osu.ppy.sh/docs/#get-user
        :param user: ID of the user
        :param ruleset: Ruleset of the scores to be returned
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/users/{user}{str() if not ruleset else f"/{ruleset}"}",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.User(request_data)
        else:
            raise Exception(request_data)

    def get_score(self, score: int) -> models.Score | None:
        """
        This endpoint returns the detail of specified score

        osu! documentation: https://osu.ppy.sh/docs/#get-apiv2scoresrulesetorscorescore
        :param score: ID of the score
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/scores/{score}",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.Score(request_data)
        else:
            raise Exception(request_data)

    def get_latest_score(
            self,
            user: int,
            ruleset: str,
            include_fails: bool = False,
            legacy_only: bool = False,
    ) -> models.Score | None:
        """
        This endpoint returns the latest score of specified user

        osu! documentation: https://osu.ppy.sh/docs/#get-user-scores
        :param user: ID of the user
        :param ruleset: Ruleset of the scores to be returned
        :param include_fails: Include scores of failed plays
        :param legacy_only: Whether or not to exclude lazer scores
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/users/{user}/scores/recent",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
                json={
                    "legacy_only": int(legacy_only),
                    "include_fails": int(include_fails),
                    "mode": ruleset,
                    "limit": 1,
                },
            ).prepare(),
        )
        request_data = request.json()
        if isinstance(request_data, list):
            try:
                return models.Score(request_data[int()])
            except IndexError:
                return None
        else:
            raise Exception(request_data)

    def get_best_scores(self, user: int, ruleset: str, legacy_only: bool = False) -> list[models.Score] | None:
        """
        This endpoint returns the best scores of specified user

        osu! documentation: https://osu.ppy.sh/docs/#get-user-scores
        :param user: ID of the user
        :param ruleset: Ruleset of the scores to be returned
        :param legacy_only: Whether or not to exclude lazer scores
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/users/{user}/scores/best",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
                json={
                    "legacy_only": int(legacy_only),
                    "mode": ruleset,
                    "limit": 100,
                },
            ).prepare(),
        )
        request_data = request.json()
        if isinstance(request_data, list):
            return [models.Score(score_data) for score_data in request_data]
        else:
            raise Exception(request_data)

    def get_beatmap(self, beatmap: int) -> models.Beatmap | None:
        """
        Gets beatmap data for the specified beatmap ID

        osu! documentation: https://osu.ppy.sh/docs/#get-beatmap
        :param beatmap: ID of the beatmap
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/beatmaps/{beatmap}",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.Beatmap(request_data)
        else:
            raise Exception(request_data)

    def get_beatmap_attributes(
            self,
            beatmap: int,
            mods: list[dict] = None,
            ruleset: str = None,
    ) -> models.BeatmapAttributes | None:
        """
        Returns difficulty attributes of beatmap with specific mode and mods combination

        osu! documentation: https://osu.ppy.sh/docs/#get-beatmap-attributes
        :param beatmap: ID of the beatmap
        :param mods: Mod combination
        :param ruleset: Ruleset of the difficulty attributes
        """

        request = self._query_helper(
            request=requests.Request(
                method="POST",
                url=f"{self._BASE_URL}/beatmaps/{beatmap}/attributes",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
                json={
                    "mods": mods,
                    "ruleset": ruleset,
                },
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.BeatmapAttributes(request_data)
        else:
            raise Exception(request_data)

    def get_beatmapset(self, beatmapset: int) -> models.Beatmapset | None:
        """
        This endpoint returns the detail of specified beatmapset

        osu! documentation: https://osu.ppy.sh/docs/#get-apiv2beatmapsetsbeatmapset
        :param beatmapset: ID of the beatmapset
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/beatmapsets/{beatmapset}",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.Beatmapset(request_data)
        else:
            raise Exception(request_data)

    def get_seasonal_backgrounds(self) -> models.SeasonalBackgroundSetContainer | None:
        """
        This endpoint returns current seasonal backgrounds

        osu! documentation: https://osu.ppy.sh/docs/#get-apiv2seasonal-backgrounds
        """

        request = self._query_helper(
            request=requests.Request(
                method="GET",
                url=f"{self._BASE_URL}/seasonal-backgrounds",
                headers=self._get_headers(include_api_version=True, include_authorization=True),
            ).prepare(),
        )
        request_data = request.json()
        if self._check_failure_keys(request_data):
            return models.SeasonalBackgroundSetContainer(request_data)
        else:
            raise Exception(request_data)
