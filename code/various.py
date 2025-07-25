import rosu_pp_py, sys, os
import models


def get_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ScoreWeight:
    index: int | None
    score: models.Score | None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def get_score_weight(score: models.Score, best_scores: list[models.Score]) -> ScoreWeight | None:
    for best_score in best_scores:
        if best_score.id == score.id:
            return ScoreWeight(index=best_scores.index(best_score) + 1, score=best_score)
    return None


class RecalculatedPerformance:
    fc: rosu_pp_py.PerformanceAttributes | None
    ss: rosu_pp_py.PerformanceAttributes | None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def calculate_pp(score: models.Score, beatmap_raw: models.RawBeatmapContainer, lazer_mode: bool) -> RecalculatedPerformance | None:
    beatmap = rosu_pp_py.Beatmap(bytes=beatmap_raw.bytes)
    filtered_mods = score.mods if score.mods else [str()]
    mods_string = str().join(filtered_mods)
    ruleset = models.Rulesets.index[score.ruleset_id]
    beatmap.convert(mode=models.Rulesets.rosu_pp[ruleset], mods=mods_string)
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
        return RecalculatedPerformance(
            fc=rosu_pp_py.Performance(mods=mods_string, lazer=lazer_mode, **fc_kwargs).calculate(beatmap),
            ss=rosu_pp_py.Performance(mods=mods_string, lazer=lazer_mode).calculate(beatmap),
        )
    except:
        return None
