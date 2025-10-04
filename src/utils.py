from __future__ import annotations
import rosu_pp_py, spectra
import models


def get_score_weight(score: models.Score, best_scores: list[models.Score]) -> models.ScoreWeightValues | None:
    for i, best_score in enumerate(best_scores, start=1):
        if best_score.id == score.id:
            return models.ScoreWeightValues(place=i, score=best_score)
    return None


def calculate_pp(
        score: models.Score,
        beatmap_raw: models.RawBeatmapContainer,
        lazer_mode: bool,
) -> models.RecalculatedValues | None:
    beatmap = rosu_pp_py.Beatmap(bytes=beatmap_raw.bytes)
    ruleset = models.RulesetsUtils.list[score.ruleset_id]
    beatmap.convert(mode=models.RulesetsUtils.rosu_pp.get(ruleset), mods=score.mods.data)
    fc_kwargs = {
        models.RulesetsType.OSU: {
            "n100": score.statistics.ok,
            "n50": score.statistics.meh,
        },
        models.RulesetsType.TAIKO: {
            "n100": score.statistics.ok,
        },
        models.RulesetsType.CATCH: {
            "n100": score.statistics.large_tick_hit,
            "n50": score.statistics.small_tick_hit,
        },
        models.RulesetsType.MANIA: {
            "n300": score.statistics.great,
            "n_katu": score.statistics.good,
            "n100": score.statistics.ok,
            "n50": score.statistics.meh,
        },
    }.get(ruleset, None)
    if not fc_kwargs:
        return fc_kwargs
    try:
        return models.RecalculatedValues(
            performance_fc=rosu_pp_py.Performance(
                mods=score.mods.data,
                lazer=lazer_mode,
                **fc_kwargs,
            ).calculate(beatmap),
            performance_ss=rosu_pp_py.Performance(
                mods=score.mods.data,
                lazer=lazer_mode,
            ).calculate(beatmap),
            difficulty=rosu_pp_py.Difficulty(
                mods=score.mods.data,
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
            [spectra.html(i[1]).to("rgb") for i in spectrum_values],
        ).domain(
            [i[0] for i in spectrum_values],
        )(difficulty).color_object.get_rgb_hex().upper(),
        text_color=maximum_value if difficulty < 6.5 else gold_text_value,
    )
