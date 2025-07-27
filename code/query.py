from __future__ import annotations
import requests, datetime, logging, sys
import models, data


def check_for_updates(version: str, beta: bool = False) -> bool | None:
    try:
        return not beta and requests.get("https://github.com/diquoks/osu-parser/releases/latest").url != f"https://github.com/diquoks/osu-parser/releases/tag/{version}"
    except:
        return None


class OAuthApplication:
    _ENDPOINT_URL = "https://{0}.ppy.sh"
    _FAILURE_KEYS = {"error", "authentication"}
    _DEBUG_STRING = "{0}: {1}"

    def __init__(self, client_id: int, client_secret: str, redirect_uri: str, scopes: str, server: str = "osu") -> None:
        self._ENDPOINT_URL = self._ENDPOINT_URL.format(server)
        self._BASE_URL = f"{self._ENDPOINT_URL}/api/v2"
        self._OAUTH_URL = f"{self._ENDPOINT_URL}/oauth"
        self._RAW_URL = f"{self._ENDPOINT_URL}/osu"
        self._registry = data.ApplicationRegistry()
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        super().__init__()

    @classmethod
    def _add_method(cls):
        return lambda func: setattr(cls, func.__name__, func)

    @classmethod
    def from_config(cls, config: data.ApplicationConfig.OAuthConfig) -> OAuthApplication:
        return cls(config.client_id, config.client_secret, config.redirect_uri, config.scopes, config.server)

    @staticmethod
    def convert_expire_date(json_data: dict) -> dict:
        json_data.update({"expires_in": int((datetime.datetime.now() + datetime.timedelta(seconds=json_data["expires_in"])).timestamp())})
        return json_data

    @staticmethod
    def extract_expire_date(json_data: dict) -> dict | None:
        json_data.update({"expires_in": datetime.datetime.fromtimestamp(json_data["expires_in"])})
        return json_data

    def _query_helper(self) -> None:
        self._registry.refresh()
        logging.debug(self._DEBUG_STRING.format(sys._getframe().f_code.co_name, "Succeeded self._registry.refresh()"))
        if (self._registry.oauth.expires_in and self._registry.oauth.expires_in < datetime.datetime.now().timestamp()) or None in self._registry.oauth.values().values():
            logging.debug(self._DEBUG_STRING.format(sys._getframe().f_code.co_name, "Scheduled refresh_access_token()"))
            self.refresh_access_token(refresh_token=self._registry.oauth.refresh_token)
            logging.debug(self._DEBUG_STRING.format(sys._getframe().f_code.co_name, "Succeeded refresh_access_token()"))

    def get_raw_beatmap(self, beatmap: int) -> models.RawBeatmapContainer | None:
        """
        Endpoint to retrieve ``.osu`` difficulty files
        :param beatmap: ID of the beatmap
        """
        request = requests.get(
            url=f"{self._RAW_URL}/{beatmap}"
        )
        return models.RawBeatmapContainer(id=beatmap, bytes=request.content) if request.content else None

    def get_auth_url(self) -> str:
        """
        https://osu.ppy.sh/docs/#authorization-code-grant
        :return: URL for authorization
        """
        request = requests.get(
            url=f"{self._OAUTH_URL}/authorize",
            params={
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "scope": self.scopes,
            },
        )
        return request.url

    def get_access_token(self, code: str) -> bool | None:
        """
        https://osu.ppy.sh/docs/#authorization-code-grant
        :param code: The code you received
        :return: ``True`` if authorization was successful
        """
        request = requests.post(
            url=f"{self._OAUTH_URL}/token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            self._registry.oauth.update(**self.convert_expire_date(request_data))
            return True
        else:
            raise Exception(request_data)

    def refresh_access_token(self, refresh_token: str) -> bool | None:
        """
        https://osu.ppy.sh/docs/#authorization-code-grant
        :param refresh_token: Value of refresh token received from previous access token request
        :return: ``True`` if refreshing was successful
        """
        request = requests.post(
            url=f"{self._OAUTH_URL}/token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": self.scopes,
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            self._registry.oauth.update(**self.convert_expire_date(request_data))
            return True
        else:
            raise Exception(request_data)

    def revoke_current_token(self) -> bool | None:
        """
        https://osu.ppy.sh/docs/#revoke-current-token
        :return: ``True`` if revocation was successful
        """
        self._query_helper()
        request = requests.delete(
            url=f"{self._BASE_URL}/oauth/tokens/current",
            headers={
                "Accept": "application/json",
                "Content-Type": "Accept: application/json",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
        )
        try:
            request.json()
        except:
            return True
        else:
            raise Exception(request)

    def get_own_data(self, ruleset: str = None) -> models.User | None:
        """
        https://osu.ppy.sh/docs/#get-own-data
        :param ruleset: https://osu.ppy.sh/docs/#ruleset User default mode will be used if not specified
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/me{str() if ruleset is None else f"/{ruleset}"}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            return models.User(data=request_data)
        else:
            raise Exception(request_data)

    def get_user(self, user: int, ruleset: str = None) -> models.User | None:
        """
        https://osu.ppy.sh/docs/#get-user
        :param user: Id or ``@``-prefixed username of the user
        :param ruleset: https://osu.ppy.sh/docs/#ruleset User default mode will be used if not specified
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/users/{user}{str() if ruleset is None else f"/{ruleset}"}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            return models.User(data=request_data)
        else:
            raise Exception(request_data)

    def get_score(self, score: int) -> models.Score | None:
        """
        https://osu.ppy.sh/docs/#get-apiv2scoresrulesetorscorescore
        :param score: ID of the score
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/scores/{score}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            return models.Score(data=request_data)
        else:
            raise Exception(request_data)

    def get_latest_score(self, user: int, ruleset: str, include_fails: bool = False, legacy_only: bool = False) -> models.Score | None:
        """
        https://osu.ppy.sh/docs/#get-user-scores
        :param user: Id of the user
        :param ruleset: https://osu.ppy.sh/docs/#ruleset User default mode will be used if not specified
        :param include_fails: Include scores of failed plays
        :param legacy_only: Whether or not to exclude lazer scores
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/users/{user}/scores/recent",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
            params={
                "legacy_only": int(legacy_only),
                "include_fails": int(include_fails),
                "mode": ruleset,
                "limit": 1,
            },
        )
        request_data = request.json()
        try:
            if isinstance(request_data, list) and len(self._FAILURE_KEYS & set(list(request_data[int()].keys()))) == int():
                return models.Score(data=request_data[int()])
            else:
                raise Exception(request_data)
        except IndexError:
            return None

    def get_best_scores(self, user: int, ruleset: str, legacy_only: bool = False) -> list[models.Score] | None:
        """
        https://osu.ppy.sh/docs/#get-user-scores
        :param user: Id of the user
        :param ruleset: https://osu.ppy.sh/docs/#ruleset User default mode will be used if not specified
        :param legacy_only: Whether or not to exclude lazer scores
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/users/{user}/scores/best",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
            params={
                "legacy_only": int(legacy_only),
                "mode": ruleset,
                "limit": 100,
            },
        )
        request_data = request.json()
        if isinstance(request_data, list) and len(self._FAILURE_KEYS & set(list(request_data[int()].keys()))) == int():
            return [models.Score(data=i) for i in request_data]
        else:
            raise Exception(request_data)

    def get_beatmap(self, beatmap: int) -> models.Beatmap | None:
        """
        https://osu.ppy.sh/docs/#get-beatmap
        :param beatmap: ID of the beatmap
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/beatmaps/{beatmap}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            return models.Beatmap(data=request_data)
        else:
            raise Exception(request_data)

    def get_beatmap_attributes(self, beatmap: int, mods: list = None, ruleset: str = None) -> models.BeatmapAttributes | None:
        """
        https://osu.ppy.sh/docs/#get-beatmap-attributes
        :param beatmap: ID of the beatmap
        :param mods: Mod combination
        :param ruleset: https://osu.ppy.sh/docs/#ruleset Defaults to ruleset of the specified beatmap
        """
        self._query_helper()
        request = requests.post(
            url=f"{self._BASE_URL}/beatmaps/{beatmap}/attributes",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
            params={
                "mods[]": mods,
                "ruleset": ruleset,
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            return models.BeatmapAttributes(data=request_data)
        else:
            raise Exception(request_data)

    def get_beatmapset(self, beatmapset: int) -> models.Beatmapset | None:
        """
        https://osu.ppy.sh/docs/#get-apiv2beatmapsetsbeatmapset
        :param beatmapset: ID of the beatmapset
        """
        self._query_helper()
        request = requests.get(
            url=f"{self._BASE_URL}/beatmapsets/{beatmapset}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-version": "20240529",
                "Authorization": f"{self._registry.oauth.token_type} {self._registry.oauth.access_token}",
            },
        )
        request_data = request.json()
        if len(self._FAILURE_KEYS & set(list(request_data.keys()))) == int():
            return models.Beatmapset(data=request_data)
        else:
            raise Exception(request_data)
