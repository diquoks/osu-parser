import logging

import pyquoks

import src.data
import src.query
import tests._test_utils


class TestQuery(pyquoks.test.TestCase):
    _MODULE_NAME = __name__

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        config_manager = tests._test_utils.ConfigManager()

        cls._client = src.query.OAuthClient(
            config_manager=config_manager,
            logger_service=src.data.LoggerService(
                filename=src.query.__name__,
                file_handling=config_manager.settings.file_logging,
                level=logging.DEBUG if config_manager.settings.debug else logging.INFO,
                path=pyquoks.utils.get_path("tests/logs/"),
            ),
        )
