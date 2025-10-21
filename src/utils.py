from __future__ import annotations
import rosu_pp_py, spectra
import models


def get_score_weight(score: models.Score, best_scores: list[models.Score]) -> models.ScoreWeightValues | None:
    for place, best_score in enumerate(best_scores, start=1):
        if best_score.id == score.id:
            return models.ScoreWeightValues(place=place, score=best_score)
    return None


def _get_fc_kwargs(ruleset: models.RulesetsType, score: models.Score) -> dict | None:
    match ruleset:
        case models.RulesetsType.OSU:
            return {
                "n100": score.statistics.ok,
                "n50": score.statistics.meh,
            }
        case models.RulesetsType.TAIKO:
            return {
                "n100": score.statistics.ok,
            }
        case models.RulesetsType.CATCH:
            return {
                "n100": score.statistics.large_tick_hit,
                "n50": score.statistics.small_tick_hit,
            }
        case models.RulesetsType.MANIA:
            return {
                "n300": score.statistics.great,
                "n_katu": score.statistics.good,
                "n100": score.statistics.ok,
                "n50": score.statistics.meh,
            }


def calculate_pp(
        score: models.Score,
        beatmap_raw: models.RawBeatmapContainer,
        lazer_mode: bool,
) -> models.RecalculatedValues | None:
    beatmap = rosu_pp_py.Beatmap(bytes=beatmap_raw.bytes)
    ruleset = models.RulesetsUtils.list[score.ruleset_id]
    beatmap.convert(mode=models.RulesetsUtils.rosu_pp.get(ruleset), mods=score.mods._data)
    try:
        return models.RecalculatedValues(
            performance_fc=rosu_pp_py.Performance(
                mods=score.mods._data,
                lazer=lazer_mode,
                **_get_fc_kwargs(ruleset, score),
            ).calculate(beatmap),
            performance_ss=rosu_pp_py.Performance(
                mods=score.mods._data,
                lazer=lazer_mode,
            ).calculate(beatmap),
            difficulty=rosu_pp_py.Difficulty(
                mods=score.mods._data,
                lazer=lazer_mode,
            ).calculate(beatmap),
        )
    except:
        return None


def get_difficulty_colors(difficulty: float) -> models.DifficultyColorsValues:
    gold_text_value = "#FFD966"
    minimum_value = "#AAAAAA"
    maximum_value = "#000000"
    spectrum_values = [
        [0.10, "#4290FF"],
        [1.25, "#4FC0FF"],
        [2.00, "#4FFFD5"],
        [2.50, "#7CFF4F"],
        [3.30, "#F6F05C"],
        [4.20, "#FF8068"],
        [4.90, "#FF4E6F"],
        [5.80, "#C645B8"],
        [6.70, "#6563DE"],
        [7.70, "#18158E"],
        [9.00, "#000000"],
    ]
    return models.DifficultyColorsValues(
        difficulty_color=minimum_value if difficulty < 0.1 else maximum_value if difficulty > 9 else spectra.scale(
            [spectra.html(stop_point[1]).to("rgb") for stop_point in spectrum_values],
        ).domain(
            [stop_point[0] for stop_point in spectrum_values],
        )(difficulty).color_object.get_rgb_hex().upper(),
        text_color=maximum_value if difficulty < 6.5 else gold_text_value,
    )
