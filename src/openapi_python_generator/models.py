from typing import List
from typing import Optional

from openapi_schema_pydantic import Operation
from openapi_schema_pydantic import PathItem
from openapi_schema_pydantic import Schema
from pydantic import BaseModel


class LibraryConfig(BaseModel):
    name: str
    library_name: str
    template_name: str
    include_async: bool
    include_sync: bool


class TypeConversion(BaseModel):
    original_type: str
    converted_type: str
    import_types: Optional[List[str]] = None


class OpReturnType(BaseModel):
    type: Optional[TypeConversion] = None
    status_code: int
    complex_type: bool = False
    list_type: Optional[str] = None


class ServiceOperation(BaseModel):
    params: str
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
    method: str
    use_orjson: bool = False


class Property(BaseModel):
    name: str
    type: TypeConversion
    required: bool
    default: Optional[str]
    import_type: Optional[List[str]] = None


class Model(BaseModel):
    file_name: str
    content: str
    openapi_object: Schema
    properties: List[Property] = []


class Service(BaseModel):
    file_name: str
    operations: List[ServiceOperation]
    content: str
    async_client: Optional[bool] = False
    library_import: str
    use_orjson: bool = False


class APIConfig(BaseModel):
    file_name: str
    base_url: str
    content: str


class ConversionResult(BaseModel):
    models: List[Model]
    services: List[Service]
    api_config: APIConfig
