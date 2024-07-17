from typing import *

from pydantic import BaseModel, Field

from .IcolorRead import IcolorRead
from .IcompositionRead import IcompositionRead
from .IparameterRead import IparameterRead
from .IproductOptionRead import IproductOptionRead
from .IwholesaleOptionRead import IwholesaleOptionRead
from .ProductStatusEnum import ProductStatusEnum


class IproductRead(BaseModel):
    """
    IProductRead model

    """

    name: Optional[str] = Field(alias="name", default=None)

    description: Optional[str] = Field(alias="description", default=None)

    images: Optional[List[str]] = Field(alias="images", default=None)

    thumbnail_images: Optional[List[str]] = Field(alias="thumbnail_images", default=None)

    id: str = Field(alias="id")

    parameters: Optional[List[Optional[IparameterRead]]] = Field(alias="parameters", default=None)

    options: Optional[List[Optional[IproductOptionRead]]] = Field(alias="options", default=None)

    wholesale_options: Optional[List[Optional[IwholesaleOptionRead]]] = Field(alias="wholesale_options", default=None)

    compositions: Optional[List[Optional[IcompositionRead]]] = Field(alias="compositions", default=None)

    colors: Optional[List[Optional[IcolorRead]]] = Field(alias="colors", default=None)

    status: ProductStatusEnum = Field(alias="status")

    post_url: str = Field(alias="post_url")
