from typing import List, Optional

from openapi_schema_pydantic import Schema, PathItem, Operation
from pydantic import BaseModel

class ServiceOperation(BaseModel):
    params : List[str]
    operation_id : str
    query_params : List[str]
    return_type : str
    operation : Operation
    pathItem : PathItem
    content : str
    async_client : Optional[bool] = False
    tag : Optional[str] = None

class Property(BaseModel):
    name: str
    type: str
    required: bool
    default: Optional[str]


class Model(BaseModel):
    file_name: str
    content: str
    openapi_object: Schema
    references: List[str] = []
    properties: List[Property] = []


class Service(BaseModel):
    file_name: str
    operations : List[ServiceOperation]
    imports : List[str]
    content : str
    async_client : Optional[bool] = False


class ConversionResult(BaseModel):
    models: List[Model]
    services: List[Service]
