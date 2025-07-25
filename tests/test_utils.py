import unittest, logging, types, sys

sys.path.append('../code')
import models, query, data


class SampleTest(unittest.TestCase):
    _REFRESH_TOKEN: bool

    @classmethod
    def setUpClass(cls) -> None:
        cls._registry = data.ApplicationRegistry()
        cls._config = data.ApplicationConfig()
        cls._oauth = query.OAuthApplication.from_config(cls._config.oauth)
        logging.basicConfig(level=logging.DEBUG if cls._config.settings.beta else logging.INFO)
        if cls._REFRESH_TOKEN:
            try:
                cls._oauth._query_helper()
            except:
                raise unittest.SkipTest("access_token wasn't updated")

    def assert_type(self, test_data: object, test_type: type | types.UnionType) -> None:
        print(test_data)
        if isinstance(test_data, models.SampleModel):
            for i in list(test_data.data.keys()):
                print(f"{i}: {test_data.data[i]}")
        self.assertIsInstance(test_data, test_type)
