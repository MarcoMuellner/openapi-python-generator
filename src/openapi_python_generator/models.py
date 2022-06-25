from typing import List, Optional

from openapi_schema_pydantic import Schema, PathItem, Operation
from pydantic import BaseModel


class OpReturnType(BaseModel):
    type: str
    status_code: int
    complex_type: bool = False


class ServiceOperation(BaseModel):
    params: List[str]
    operation_id: str
    query_params: List[str]
    return_type: OpReturnType
    operation: Operation
    pathItem: PathItem
    content: str
    async_client: Optional[bool] = False
    tag: Optional[str] = None
    path_name: str
    body_param: Optional[str] = None


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
    operations: List[ServiceOperation]
    content: str
    async_client: Optional[bool] = False


class APIConfig(BaseModel):
    file_name: str
    content: str


class ConversionResult(BaseModel):
    models: List[Model]
    services: List[Service]
    api_config: APIConfig
