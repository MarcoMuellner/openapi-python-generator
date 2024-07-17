from typing import *

from pydantic import BaseModel, Field


class InextCursor(BaseModel):
    """
    INextCursor model

    """

    offset: int = Field(alias="offset")

    limit: int = Field(alias="limit")
