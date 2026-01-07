import logging

import pyquoks

import src.data
import src.models
import src.query
import tests._test_utils


class TestQuery(pyquoks.test.TestCase):
    _MODULE_NAME = __name__

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        environment_provider = src.data.EnvironmentProvider()
        config_manager = tests._test_utils.ConfigManager()

        cls._config = config_manager
        cls._client = src.query.OAuthClient(
            environment_provider=environment_provider,
            config_manager=config_manager,
            logger_service=src.data.LoggerService(
                filename=src.query.__name__,
                file_handling=config_manager.settings.file_logging,
                level=logging.DEBUG if config_manager.settings.debug else logging.INFO,
                path=pyquoks.utils.get_path("tests/logs/"),
            ),
        )

        cls._USER_ID = 31760756
        cls._RULESET = src.models.Ruleset.OSU
        cls._BEATMAP_ID = 75
        cls._BEATMAPSET_ID = 1
        cls._SCORE_ID = 6016860181

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        cls._config.oauth.update(
            access_token="",
            expires_timestamp=0,
        )

    def test_get_raw_beatmap(self) -> None:
        current_raw_beatmap = self._client.get_raw_beatmap(
            beatmap_id=self._BEATMAP_ID,
        )

        self.assert_type(
            func_name=self.test_get_raw_beatmap.__name__,
            test_data=current_raw_beatmap,
            test_type=src.models.RawBeatmap,
        )

    def test_authorize_client(self) -> None:
        self._client.authorize_client()

        self.assert_type(
            func_name=self.test_authorize_client.__name__,
            test_data=self._config.oauth.access_token,
            test_type=str,
        )

        self.assert_type(
            func_name=self.test_authorize_client.__name__,
            test_data=self._config.oauth.expires_timestamp,
            test_type=int,
        )

    def test_get_user(self) -> None:
        current_user = self._client.get_user(
            user_id=self._USER_ID,
            ruleset=self._RULESET,
        )

        self.assert_type(
            func_name=self.test_get_user.__name__,
            test_data=current_user,
            test_type=src.models.UserExtended,
        )

    def test_get_score(self) -> None:
        current_score = self._client.get_score(
            score_id=self._SCORE_ID,
        )

        self.assert_type(
            func_name=self.test_get_user.__name__,
            test_data=current_score,
            test_type=src.models.Score,
        )

    def test_get_latest_user_score(self) -> None:
        current_score = self._client.get_latest_user_score(
            user_id=self._USER_ID,
            ruleset=self._RULESET,
        )

        self.assert_type(
            func_name=self.test_get_latest_user_score.__name__,
            test_data=current_score,
            test_type=src.models.Score | None,
        )
