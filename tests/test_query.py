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

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        cls._config.oauth.update(
            access_token="",
            expires_timestamp=0,
        )

    def test_get_raw_beatmap(self) -> None:
        self.assert_type(
            func_name=self.test_get_raw_beatmap.__name__,
            test_data=self._client.get_raw_beatmap(
                beatmap_id=75,
            ),
            test_type=src.models.RawBeatmap,
        )

    def test_get_access_token(self) -> None:
        self._client.get_access_token()

        self.assert_type(
            func_name=self.test_get_access_token.__name__,
            test_data=self._config.oauth.access_token,
            test_type=str,
        )

        self.assert_type(
            func_name=self.test_get_access_token.__name__,
            test_data=self._config.oauth.expires_timestamp,
            test_type=int,
        )
