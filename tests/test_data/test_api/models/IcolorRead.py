from typing import *

from pydantic import BaseModel, Field


class IcolorRead(BaseModel):
    """
    IColorRead model

    """

    name: str = Field(alias="name")
