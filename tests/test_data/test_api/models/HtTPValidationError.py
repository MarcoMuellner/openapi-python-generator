from typing import *

from pydantic import BaseModel, Field

from .ValidationError import ValidationError


class HtTPValidationError(BaseModel):
    """
    HTTPValidationError model

    """

    detail: Optional[List[Optional[ValidationError]]] = Field(alias="detail", default=None)
