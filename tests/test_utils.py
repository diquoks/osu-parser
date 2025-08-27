from __future__ import annotations
import sys

sys.path.append('../code')
import unittest, logging, types
import models, query, data, misc


class ITest(unittest.TestCase):
    _REFRESH_TOKEN: bool = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._strings = misc.Strings()
        cls._config = data.ConfigProvider()
        cls._registry = data.RegistryProvider()
        cls._oauth = query.OAuthClient.from_config(cls._config.oauth)
        logging.basicConfig(level=logging.DEBUG if cls._config.settings.beta else logging.INFO)
        if cls._REFRESH_TOKEN:
            try:
                cls._oauth._query_helper()
            except:
                raise unittest.SkipTest(cls._strings.log.error_refresh_token)

    def assert_type(self, func_name: str, test_data: object, test_type: type | types.UnionType) -> None:
        print(self._strings.debug.test_data.format(func_name, test_data, test_type))
        if isinstance(test_data, models.IModel):
            print(self._strings.separator.newline.join(self._strings.debug.attribute_data.format(k, v) for k, v in list(test_data.data.items())))
        self.assertIsInstance(test_data, test_type)
