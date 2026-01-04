import pydantic


# region Models

class RawBeatmap(pydantic.BaseModel):
    id: int
    raw: bytes

# endregion
