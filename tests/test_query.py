from __future__ import annotations
import pyquoks
import query


class TestQuery(pyquoks.test.TestCase):
    _MODULE_NAME = __name__

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls._client = query.OAuthClient()
