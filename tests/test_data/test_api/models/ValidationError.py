from typing import *

from pydantic import BaseModel, Field


class ValidationError(BaseModel):
    """
    ValidationError model

    """

    loc: List[Union[str, int]] = Field(alias="loc")

    msg: str = Field(alias="msg")

    type: str = Field(alias="type")
