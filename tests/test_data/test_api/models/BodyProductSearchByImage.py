from typing import *

from pydantic import BaseModel, Field


class BodyProductSearchByImage(BaseModel):
    """
    Body_product_search_by_image model

    """

    image: bytes = Field(alias="image")
