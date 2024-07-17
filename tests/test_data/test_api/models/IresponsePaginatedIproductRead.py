from typing import *

from pydantic import BaseModel, Field

from .InextCursor import InextCursor
from .IproductRead import IproductRead


class IresponsePaginatedIproductRead(BaseModel):
    """
    IResponsePaginated[IProductRead] model

    """

    items: List[IproductRead] = Field(alias="items")

    total: Union[int, None] = Field(alias="total")

    limit: Union[int, None] = Field(alias="limit")

    offset: Union[int, None] = Field(alias="offset")

    next: Optional[Union[InextCursor, None]] = Field(alias="next", default=None)
