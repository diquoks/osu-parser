from __future__ import annotations
import threading, unittest, sys
import test_utils, localhost

SKIP_DEPLOYMENT = True


class TestLocalhost(test_utils.ITest):
    _REFRESH_TOKEN = False

    def test_localhost(self) -> None:
        func_name = sys._getframe().f_code.co_name
        test_data = self._strings.log.debug_localhost_deploy.format(SKIP_DEPLOYMENT)
        test_type = str
        self.assert_type(func_name, test_data, test_type)
        localhost_flask = localhost.LocalhostFlask()
        localhost_thread = threading.Thread(
            target=localhost_flask.serve,
            kwargs={"port": 727},
            daemon=SKIP_DEPLOYMENT,
            name="localhostThread",
        )
        try:
            self._oauth.refresh_access_token(refresh_token=self._registry.oauth.refresh_token)
        except Exception as e:
            localhost_thread.daemon = False
            self._logger.error(self._strings.log.error_localhost_deploy.format(localhost_thread.daemon), exc_info=e)
        finally:
            localhost_thread.start()

    def test_get_auth_url(self) -> None:
        func_name = sys._getframe().f_code.co_name
        test_data = self._oauth.get_auth_url()
        test_type = str
        self.assert_type(func_name, test_data, test_type)


if __name__ == "__main__":
    unittest.main()
