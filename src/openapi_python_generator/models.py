from typing import List, Optional, Union

from openapi_pydantic.v3.v3_0 import (
    Operation as Operation30,
)
from openapi_pydantic.v3.v3_0 import (
    PathItem as PathItem30,
)
from openapi_pydantic.v3.v3_0 import (
    Schema as Schema30,
)
from openapi_pydantic.v3.v3_1 import (
    Operation as Operation31,
)
from openapi_pydantic.v3.v3_1 import (
    PathItem as PathItem31,
)
from openapi_pydantic.v3.v3_1 import (
    Schema as Schema31,
)
from pydantic import BaseModel

# Type unions for compatibility with both OpenAPI 3.0 and 3.1
Operation = Union[Operation30, Operation31]
PathItem = Union[PathItem30, PathItem31]
Schema = Union[Schema30, Schema31]


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
