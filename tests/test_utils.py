from __future__ import annotations
import unittest, logging, types
import pyquoks.models
import query, data


class ITest(unittest.TestCase):
    _REFRESH_TOKEN: bool = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._strings = data.StringsProvider()
        cls._config = data.ConfigProvider()
        cls._registry = data.RegistryManager()
        cls._oauth = query.OAuthClient(cls._config)
        cls._logger = data.LoggerService(
            name=__name__,
            file_handling=cls._config.settings.file_logging,
            level=logging.DEBUG if cls._config.settings.beta else logging.INFO,
        )
        if cls._REFRESH_TOKEN:
            try:
                cls._oauth.refresh_access_token(refresh_token=cls._registry.oauth.refresh_token)
            except:
                raise unittest.SkipTest(cls._strings.log.error_refresh_token)

    def assert_type(self, func_name: str, test_data: object, test_type: type | types.UnionType) -> None:
        self._logger.info(self._strings.debug.test_data.format(func_name, test_data, test_type))
        if isinstance(test_data, pyquoks.models.IModel):
            self._logger.info(
                self._strings.separator.newline.join([
                    self._strings.debug.attribute_data.format(k, v) for k, v in list(test_data.data.items())
                ]),
            )
        self.assertIsInstance(test_data, test_type)
