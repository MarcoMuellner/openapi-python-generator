from typing import *

from pydantic import BaseModel, Field


class IproductOptionRead(BaseModel):
    """
    IProductOptionRead model

    """

    price: Optional[str] = Field(alias="price", default=None)

    name: str = Field(alias="name")
