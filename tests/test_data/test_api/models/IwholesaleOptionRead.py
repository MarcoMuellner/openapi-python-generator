from typing import *

from pydantic import BaseModel, Field


class IwholesaleOptionRead(BaseModel):
    """
    IWholesaleOptionRead model

    """

    name: str = Field(alias="name")

    count: int = Field(alias="count")

    price: Optional[str] = Field(alias="price", default=None)
