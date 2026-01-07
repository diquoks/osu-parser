import enum
import typing

import pydantic


# region Enums

class Grade(enum.StrEnum):
    XH = "XH"
    X = "X"
    SH = "SH"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

    @property
    def readable(self) -> str:
        match self:
            case Grade.XH | Grade.X:
                return "SS"
            case Grade.SH:
                return "S"
            case _:
                return self.value

    @property
    def is_silver(self) -> bool:
        match self:
            case Grade.XH | Grade.SH:
                return True
            case _:
                return False


class Ruleset(enum.StrEnum):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#ruleset
    """

    OSU = "osu"
    TAIKO = "taiko"
    CATCH = "fruits"
    MANIA = "mania"

    @property
    def readable(self) -> str:
        match self:
            case Ruleset.OSU:
                return "osu!"
            case Ruleset.TAIKO:
                return "osu!taiko"
            case Ruleset.CATCH:
                return "osu!catch"
            case Ruleset.MANIA:
                return "osu!mania"


# endregion

# region Models

class Beatmap(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#beatmap
    """

    beatmapset_id: int
    difficulty_rating: float
    id: int
    status: str
    version: str


class BeatmapDifficultyAttributes(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#beatmapdifficultyattributes
    """

    star_rating: float
    max_combo: int


class BeatmapRaw(pydantic.BaseModel):
    id: int
    raw: bytes


class Beatmapset(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#beatmapset
    """

    artist: str
    creator: str
    id: int
    title: str


class Mod(pydantic.BaseModel):
    acronym: str
    settings: typing.Optional[dict] = None


class Score(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#score
    """

    accuracy: float
    beatmap: Beatmap
    beatmapset: Beatmapset
    id: int
    max_combo: int
    maximum_statistics: ScoreStatistics
    mods: list[Mod]
    passed: bool
    pp: typing.Optional[float] = None
    rank: Grade
    statistics: ScoreStatistics
    weight: typing.Optional[ScoreWeight] = None


class ScoreStatistics(pydantic.BaseModel):
    combo_break: int = 0
    good: int = 0
    great: int = 0
    ignore_hit: int = 0
    ignore_miss: int = 0
    large_bonus: int = 0
    large_tick_hit: int = 0
    large_tick_miss: int = 0
    meh: int = 0
    miss: int = 0
    ok: int = 0
    perfect: int = 0
    slider_tail_hit: int = 0
    small_bonus: int = 0
    small_tick_hit: int = 0
    small_tick_miss: int = 0


class ScoreWeight(pydantic.BaseModel):
    percentage: float
    pp: float


class UserExtended(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#userextended
    """

    id: int
    username: str
    playmode: Ruleset
    statistics: UserStatistics


class UserStatistics(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#userstatistics
    """

    global_rank: typing.Optional[int] = None
    pp: float

# endregion
