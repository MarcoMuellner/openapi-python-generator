from typing import *

from pydantic import BaseModel, Field


class IcompositionRead(BaseModel):
    """
    ICompositionRead model

    """

    name: str = Field(alias="name")
