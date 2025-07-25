import datetime, unittest, sys
import test_utils

sys.path.append('../code')
import models, query, data

SKIP_REVOKE = True

USER = 31760756
RULESET = models.Rulesets.MANIA
BEATMAP = 4483898
BEATMAPSET = 2126021
SCORE = 5189514128


class TestQuery(test_utils.SampleTest):
    _REFRESH_TOKEN = True

    def test_get_raw_beatmap(self) -> None:
        test_data = self._oauth.get_raw_beatmap(beatmap=BEATMAP)
        test_type = models.RawBeatmapContainer
        self.assert_type(test_data, test_type)

    def test_get_own_data(self) -> None:
        test_data = self._oauth.get_own_data()
        test_type = models.SampleModel
        self.assert_type(test_data, test_type)

    def test_get_user(self) -> None:
        test_data = self._oauth.get_user(user=USER)
        test_type = models.SampleModel
        self.assert_type(test_data, test_type)

    def test_get_score(self) -> None:
        test_data = self._oauth.get_score(score=SCORE)
        test_type = models.SampleModel
        self.assert_type(test_data, test_type)

    def test_get_latest_score(self) -> None:
        test_data = self._oauth.get_latest_score(user=USER, ruleset=RULESET)
        test_type = models.SampleModel | None
        self.assert_type(test_data, test_type)

    def test_get_best_scores(self) -> None:
        test_data = self._oauth.get_best_scores(user=USER, ruleset=RULESET)
        test_type = list | None
        self.assert_type(test_data, test_type)

    def test_get_beatmap(self) -> None:
        test_data = self._oauth.get_beatmap(beatmap=BEATMAP)
        test_type = models.SampleModel
        self.assert_type(test_data, test_type)

    def test_get_beatmapset(self) -> None:
        test_data = self._oauth.get_beatmapset(beatmapset=BEATMAPSET)
        test_type = models.SampleModel
        self.assert_type(test_data, test_type)

    def test_get_beatmap_attributes(self) -> None:
        test_data = self._oauth.get_beatmap_attributes(beatmap=BEATMAP)
        test_type = models.SampleModel
        self.assert_type(test_data, test_type)

    def test_revoke_current_token(self) -> None:
        if SKIP_REVOKE:
            raise unittest.SkipTest(f"SKIP_REVOKE = {SKIP_REVOKE}\nCurrent token revoking skipped")
        else:
            test_data = self._oauth.revoke_current_token()
            test_type = bool
            self.assert_type(test_data, test_type)


if __name__ == '__main__':
    unittest.main()
