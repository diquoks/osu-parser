from __future__ import annotations
import sys

sys.path.append('../code')
import threading, unittest
import test_utils, localhost

SKIP_DEPLOYMENT = True


class TestLocalhost(test_utils.ITest):
    _REFRESH_TOKEN = False

    def test_localhost_serve(self) -> None:
        func_name = sys._getframe().f_code.co_name
        test_data = self._strings.log.test_localhost_deploy.format(SKIP_DEPLOYMENT)
        test_type = str
        self.assert_type(func_name, test_data, test_type)
        localhost_thread = threading.Thread(target=localhost.localhost_serve, daemon=SKIP_DEPLOYMENT, name="localhostThread")
        try:
            self._oauth._query_helper()
        except:
            localhost_thread.daemon = False
            print(self._strings.log.error_localhost_deploy.format(localhost_thread.daemon))
        finally:
            localhost_thread.start()

    def test_get_auth_url(self) -> None:
        func_name = sys._getframe().f_code.co_name
        test_data = self._oauth.get_auth_url()
        test_type = str
        self.assert_type(func_name, test_data, test_type)


if __name__ == '__main__':
    unittest.main()
