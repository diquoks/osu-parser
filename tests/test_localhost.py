import threading, datetime, unittest, logging, sys
import test_utils

sys.path.append('../code')
import query, data, localhost

SKIP_DEPLOYMENT = True


class TestLocalhost(test_utils.SampleTest):
    _REFRESH_TOKEN = False

    def test_localhost_serve(self) -> None:
        test_data = f"Deploying localhost...\nlocalhost_thread.daemon = {SKIP_DEPLOYMENT}"
        print(f"{sys._getframe().f_code.co_name}:\n{test_data}\n")
        localhost_thread = threading.Thread(target=localhost.localhost_serve, daemon=SKIP_DEPLOYMENT, name="localhostThread")
        try:
            self._oauth._query_helper()
        except:
            localhost_thread.daemon = False
            print(f"Failed to refresh access token\nlocalhost_thread.daemon = {localhost_thread.daemon}")
        finally:
            localhost_thread.start()

    def test_get_auth_url(self) -> None:
        test_data = self._oauth.get_auth_url()
        test_type = str
        self.assert_type(test_data, test_type)


if __name__ == '__main__':
    unittest.main()
