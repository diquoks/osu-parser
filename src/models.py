import enum

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

    @staticmethod
    def readable(grade: Grade) -> str:
        match grade:
            case Grade.XH | Grade.X:
                return "SS"
            case Grade.SH:
                return "S"
            case Grade.S | Grade.A | Grade.B | Grade.C | Grade.D | Grade.F:
                return grade.value.upper()


class Ruleset(enum.StrEnum):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#ruleset
    """

    OSU = "osu"
    TAIKO = "taiko"
    CATCH = "fruits"
    MANIA = "mania"


# endregion

# region Models

class RawBeatmap(pydantic.BaseModel):
    id: int
    raw: bytes


class Score(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#score
    """

    accuracy: float
    max_combo: int
    passed: bool
    pp: float | None
    rank: Grade


class UserExtended(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#userextended
    """

    id: int
    username: str
    playmode: Ruleset

# endregion
