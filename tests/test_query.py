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
                path=pyquoks.utils.get_path("tests/logs/"),
            ),
        )

        cls._TEST_DATA = [
            tests._test_utils.TestData(
                beatmap_id=8708,
                beatmapset_id=184,
                message="peppy",
                ruleset=src.models.Ruleset.OSU,
                score_id=466596,
                user_id=2,
            ),
            tests._test_utils.TestData(
                beatmap_id=75,
                beatmapset_id=1,
                message="diquoks",
                ruleset=src.models.Ruleset.MANIA,
                score_id=6021181665,
                user_id=31760756,
            ),
            tests._test_utils.TestData(
                beatmap_id=557815,
                beatmapset_id=241526,
                message="empty",
                ruleset=src.models.Ruleset.OSU,
                score_id=294675820,
                user_id=7083771,
            ),
            tests._test_utils.TestData(
                beatmap_id=1811527,
                beatmapset_id=866472,
                message="osu",
                ruleset=src.models.Ruleset.OSU,
                score_id=3427873257,
                user_id=7562902,
            ),
            tests._test_utils.TestData(
                beatmap_id=5033325,
                beatmapset_id=2334877,
                message="taiko",
                ruleset=src.models.Ruleset.TAIKO,
                score_id=5614060049,
                user_id=31148838,
            ),
            tests._test_utils.TestData(
                beatmap_id=3172816,
                beatmapset_id=1552869,
                message="catch",
                ruleset=src.models.Ruleset.CATCH,
                score_id=3838127929,
                user_id=8172283,
            ),
            tests._test_utils.TestData(
                beatmap_id=5269878,
                beatmapset_id=2422085,
                message="mania",
                ruleset=src.models.Ruleset.MANIA,
                score_id=5524092839,
                user_id=19970192,
            ),
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        cls._config.oauth.update(
            access_token="",
            expires_timestamp=0,
        )

    def test_get_raw_beatmap(self) -> None:
        for test_data in self._TEST_DATA:
            current_raw_beatmap = self._client.get_raw_beatmap(
                beatmap_id=test_data.beatmap_id,
            )

            self.assert_type(
                func_name=self.test_get_raw_beatmap.__name__,
                test_data=current_raw_beatmap,
                test_type=src.models.BeatmapRaw,
                message=test_data.message,
            )

    def test_authorize_client(self) -> None:
        self._client.authorize_client()

        self.assert_type(
            func_name=self.test_authorize_client.__name__,
            test_data=self._config.oauth.access_token,
            test_type=str,
            message="access_token data in OAuthConfig",
        )

        self.assert_type(
            func_name=self.test_authorize_client.__name__,
            test_data=self._config.oauth.expires_timestamp,
            test_type=int,
            message="expires_timestamp data in OAuthConfig",
        )

    def test_get_user(self) -> None:
        for test_data in self._TEST_DATA:
            current_user = self._client.get_user(
                user_id=test_data.user_id,
                ruleset=test_data.ruleset,
            )

            self.assert_type(
                func_name=self.test_get_user.__name__,
                test_data=current_user,
                test_type=src.models.UserExtended,
                message=test_data.message,
            )

    def test_get_score(self) -> None:
        for test_data in self._TEST_DATA:
            current_score = self._client.get_score(
                score_id=test_data.score_id,
            )

            self.assert_type(
                func_name=self.test_get_score.__name__,
                test_data=current_score,
                test_type=src.models.Score,
                message=test_data.message,
            )

    def test_get_latest_user_score(self) -> None:
        for test_data in self._TEST_DATA:
            current_score = self._client.get_latest_user_score(
                user_id=test_data.user_id,
                ruleset=test_data.ruleset,
            )

            self.assert_type(
                func_name=self.test_get_latest_user_score.__name__,
                test_data=current_score,
                test_type=src.models.Score | None,
                message=test_data.message,
            )

    def test_get_best_user_scores(self) -> None:
        for test_data in self._TEST_DATA:
            current_scores = self._client.get_best_user_scores(
                user_id=test_data.user_id,
                ruleset=test_data.ruleset,
            )

            self.assert_type(
                func_name=self.test_get_best_user_scores.__name__,
                test_data=current_scores,
                test_type=list,
                message=test_data.message,
            )

            if current_scores:
                self.assert_type(
                    func_name=self.test_get_best_user_scores.__name__,
                    test_data=current_scores[0],
                    test_type=src.models.Score,
                    message=test_data.message,
                )

    def test_get_beatmap(self) -> None:
        for test_data in self._TEST_DATA:
            current_beatmap = self._client.get_beatmap(
                beatmap_id=test_data.beatmap_id,
            )

            self.assert_type(
                func_name=self.test_get_beatmap.__name__,
                test_data=current_beatmap,
                test_type=src.models.Beatmap,
                message=test_data.message,
            )

    def test_get_beatmap_attributes(self) -> None:
        for test_data in self._TEST_DATA:
            current_beatmap_attributes = self._client.get_beatmap_attributes(
                beatmap_id=test_data.beatmap_id,
            )

            self.assert_type(
                func_name=self.test_get_beatmap_attributes.__name__,
                test_data=current_beatmap_attributes,
                test_type=src.models.BeatmapDifficultyAttributes,
                message=test_data.message,
            )
