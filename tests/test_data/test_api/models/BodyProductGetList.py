from typing import *

from pydantic import BaseModel, Field


class BodyProductGetList(BaseModel):
    """
    Body_product_get_list model

    """

    compositions: Optional[List[str]] = Field(alias="compositions", default=None)

    colors: Optional[List[str]] = Field(alias="colors", default=None)

    options: Optional[List[str]] = Field(alias="options", default=None)

    seller: Optional[Union[str, None]] = Field(alias="seller", default=None)
