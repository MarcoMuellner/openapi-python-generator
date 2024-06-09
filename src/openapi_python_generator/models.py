from typing import List
from typing import Optional

from pydantic import BaseModel

import openapi_python_generator

if openapi_python_generator.OPENAPI_VERSION == "3.0":
    from openapi_pydantic.v3.v3_0_3.operation import Operation
    from openapi_pydantic.v3.v3_0_3.path_item import PathItem
    from openapi_pydantic.v3.v3_0_3.schema import Schema
else:
    from openapi_pydantic import Operation
    from openapi_pydantic import PathItem
    from openapi_pydantic import Schema


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
    header_params: List[str]
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
