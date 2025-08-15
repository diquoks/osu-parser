from __future__ import annotations
import rosu_pp_py, sys, os
import models


def get_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(path=".")
    return os.path.join(base_path, relative_path)


class IUtil:
    _ATTRIBUTES: set | None = None

    def __init__(self, **kwargs):
        for i in self._ATTRIBUTES:
            setattr(self, i, kwargs.get(i, None))


class ScoreWeight(IUtil):
    _ATTRIBUTES = {
        "place",
        "score",
    }
    place: int | None
    score: models.Score | None


def get_score_weight(score: models.Score, best_scores: list[models.Score]) -> ScoreWeight | None:
    for i, best_score in enumerate(best_scores, start=1):
        if best_score.id == score.id:
            return ScoreWeight(place=i, score=best_score)
    return None


class RecalculatedValues(IUtil):
    _ATTRIBUTES = {
        "performance_fc",
        "performance_ss",
        "difficulty",
    }
    performance_fc: rosu_pp_py.PerformanceAttributes
    performance_ss: rosu_pp_py.PerformanceAttributes
    difficulty: rosu_pp_py.DifficultyAttributes


def calculate(score: models.Score, beatmap_raw: models.RawBeatmapContainer, lazer_mode: bool) -> RecalculatedValues | None:
    beatmap = rosu_pp_py.Beatmap(bytes=beatmap_raw.bytes)
    ruleset = models.Rulesets.index[score.ruleset_id]
    beatmap.convert(mode=models.Rulesets.rosu_pp[ruleset], mods=score.mods.data)
    if ruleset == models.Rulesets.OSU:
        fc_kwargs = {"n100": score.statistics.ok, "n50": score.statistics.meh}
    elif ruleset == models.Rulesets.TAIKO:
        fc_kwargs = {"n100": score.statistics.ok}
    elif ruleset == models.Rulesets.CATCH:
        fc_kwargs = {"n100": score.statistics.large_tick_hit, "n50": score.statistics.small_tick_hit}
    elif ruleset == models.Rulesets.MANIA:
        fc_kwargs = {"n300": score.statistics.great, "n_katu": score.statistics.good, "n100": score.statistics.ok, "n50": score.statistics.meh}
    else:
        return None
    try:
        return RecalculatedValues(
            performance_fc=rosu_pp_py.Performance(mods=score.mods.data, lazer=lazer_mode, **fc_kwargs).calculate(beatmap),
            performance_ss=rosu_pp_py.Performance(mods=score.mods.data, lazer=lazer_mode).calculate(beatmap),
            difficulty=rosu_pp_py.Difficulty(mods=score.mods.data, lazer=lazer_mode).calculate(beatmap),
        )
    except:
        return None
