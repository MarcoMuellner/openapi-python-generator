from typing import *

from pydantic import BaseModel, Field


class IparameterRead(BaseModel):
    """
    IParameterRead model

    """

    name: str = Field(alias="name")

    values: Optional[List[str]] = Field(alias="values", default=None)
