from __future__ import annotations
import sys

sys.path.append('../code')
import unittest
import test_utils, models

USER = 31760756
RULESET = models.Rulesets.OSU
BEATMAP = 2419372
BEATMAPSET = 1159452
SCORE = 5214870827

SKIP_REVOKE = True


class TestQuery(test_utils.ITest):
    _REFRESH_TOKEN = True

    def test_get_raw_beatmap(self) -> None:
        test_data = self._oauth.get_raw_beatmap(beatmap=BEATMAP)
        test_type = models.RawBeatmapContainer
        self.assert_type(test_data, test_type)

    def test_get_own_data(self) -> None:
        test_data = self._oauth.get_own_data()
        test_type = models.IModel
        self.assert_type(test_data, test_type)

    def test_get_user(self) -> None:
        test_data = self._oauth.get_user(user=USER)
        test_type = models.IModel
        self.assert_type(test_data, test_type)

    def test_get_score(self) -> None:
        test_data = self._oauth.get_score(score=SCORE)
        test_type = models.IModel
        self.assert_type(test_data, test_type)

    def test_get_latest_score(self) -> None:
        test_data = self._oauth.get_latest_score(user=USER, ruleset=RULESET)
        test_type = models.IModel | None
        self.assert_type(test_data, test_type)

    def test_get_best_scores(self) -> None:
        test_data = self._oauth.get_best_scores(user=USER, ruleset=RULESET)
        test_type = list | None
        self.assert_type(test_data, test_type)

    def test_get_beatmap(self) -> None:
        test_data = self._oauth.get_beatmap(beatmap=BEATMAP)
        test_type = models.IModel
        self.assert_type(test_data, test_type)

    def test_get_beatmapset(self) -> None:
        test_data = self._oauth.get_beatmapset(beatmapset=BEATMAPSET)
        test_type = models.IModel
        self.assert_type(test_data, test_type)

    def test_get_beatmap_attributes(self) -> None:
        test_data = self._oauth.get_beatmap_attributes(beatmap=BEATMAP)
        test_type = models.IModel
        self.assert_type(test_data, test_type)

    def test_revoke_current_token(self) -> None:
        if SKIP_REVOKE:
            raise unittest.SkipTest(self._strings.log.test_revoke_token.format(SKIP_REVOKE))
        else:
            test_data = self._oauth.revoke_current_token()
            test_type = bool
            self.assert_type(test_data, test_type)


if __name__ == '__main__':
    unittest.main()
