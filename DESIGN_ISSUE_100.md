# Enhanced Error Handling for OpenAPI Python Generator

**Issue**: #100
**Status**: Design Phase
**Version**: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Patterns](#api-patterns)
5. [Error Model Parsing](#error-model-parsing)
6. [Code Generation](#code-generation)
7. [Usage Examples](#usage-examples)
8. [Implementation Plan](#implementation-plan)
9. [Appendices](#appendices)

---

## Overview

### Purpose

Enhance generated OpenAPI clients with rich error handling that provides:

- Structured exception types with full HTTP context
- Automatic parsing of error response models from OpenAPI specs
- Dual API pattern: simple (ergonomic) and detailed (full control)
- Type-safe error handling without Union type overhead
- Support for all OpenAPI 3.x response patterns

### Design Goals

1. **Rich Context**: Every error contains status code, headers, request ID, raw body, and parsed model
2. **Spec Fidelity**: Support all OpenAPI features (multiple success codes, wildcards, error schemas)
3. **Type Safety**: Direct model returns, no `Union[Success, Error]` types
4. **Backwards Compatible**: Existing code continues to work
5. **Client Agnostic**: Works with httpx, requests, and aiohttp

### Core Principles

**Exceptions for Errors, Models for Success**

- Success responses (2xx): Return Pydantic models directly
- Error responses (4xx/5xx): Raise typed exceptions with full context
- No Union types mixing success and error cases

**Dual API Pattern**

- Simple API: Direct model returns, ergonomic for common cases
- Detailed API: Response wrapper with metadata for complex scenarios

**Full OpenAPI Support**

- Multiple success status codes (200, 201, 204)
- Wildcard patterns (2XX, 4XX, 5XX)
- Different models per status code
- Error response schemas

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Generated Client                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐         ┌──────────────────┐            │
│  │  Simple API    │         │  Detailed API    │            │
│  │                │         │                  │            │
│  │  get_user()    │         │  get_user_       │            │
│  │  → User        │         │    detailed()    │            │
│  │                │         │  → Detailed      │            │
│  └────────┬───────┘         │    Response[T]   │            │
│           │                 └────────┬─────────┘            │
│           │                          │                       │
│           └──────────┬───────────────┘                       │
│                      │                                       │
│              ┌───────▼────────┐                              │
│              │ HTTP Request   │                              │
│              │ (httpx/etc)    │                              │
│              └───────┬────────┘                              │
│                      │                                       │
│         ┌────────────▼─────────────┐                         │
│         │  Success?                │                         │
│         └──┬────────────────────┬──┘                         │
│            │ Yes (2xx)          │ No (4xx/5xx)               │
│            │                    │                            │
│    ┌───────▼──────┐     ┌──────▼────────────────┐           │
│    │ Parse Model  │     │ _create_error_from_   │           │
│    │ Return Data  │     │   response()          │           │
│    └──────────────┘     │                       │           │
│                         │ - Extract metadata    │           │
│                         │ - Parse error_model   │           │
│                         │ - Create exception    │           │
│                         └──────┬────────────────┘           │
│                                │                            │
│                         ┌──────▼────────┐                   │
│                         │ Raise          │                   │
│                         │ ClientError or │                   │
│                         │ ServerError    │                   │
│                         └────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Layers

**Layer 1: Exception Types**
Core exception hierarchy with rich context attributes.

**Layer 2: Response Wrappers**
DetailedResponse class for success metadata access.

**Layer 3: Generated Operations**
Simple and detailed API variants for each operation.

**Layer 4: Utilities**
Helper functions for unwrapping, type narrowing, pattern matching.

---

## Core Components

### 1. Exception Hierarchy

A minimal three-level hierarchy providing full error context:

```python
APIError (base)
├── ClientError (4xx)
└── ServerError (5xx)
```

**Design Rationale**: Keep hierarchy flat to avoid naming conflicts with spec-defined error models (e.g., spec might have `ValidationError` model).

#### APIError Class

```python
class APIError(Exception):
    """
    Base exception for all API errors.

    Attributes:
        status_code: HTTP status code (404, 500, etc.)
        message: Human-readable error message
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        request_id: Request/correlation ID from headers
        response_headers: Complete response header dict
        response_body: Full response body text (not truncated)
        error_model: Parsed Pydantic model from OpenAPI spec (optional)
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        *,  # Keyword-only for backwards compatibility
        method: Optional[str] = None,
        url: Optional[str] = None,
        request_id: Optional[str] = None,
        response_headers: Optional[Dict[str, str]] = None,
        response_body: Optional[str] = None,
        error_model: Optional[BaseModel] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.method = method
        self.url = url
        self.request_id = request_id
        self.response_headers = response_headers or {}
        self.response_body = response_body  # Full body stored
        self.error_model = error_model

    def __str__(self) -> str:
        """Rich error message (truncates body only for display)."""
        if self.method and self.url:
            parts = [f"{self.method} {self.url} failed with status {self.status_code}"]

            if self.request_id:
                parts.append(f"(request_id: {self.request_id})")

            if self.error_model:
                parts.append(f"- {self.error_model}")
            elif self.response_body:
                # Truncate ONLY for display, not storage
                preview = self.response_body[:200]
                if len(self.response_body) > 200:
                    preview += "..."
                parts.append(f"- {preview}")

            return " ".join(parts)
        else:
            # Backwards compatible format
            return f"{self.status_code} {self.message}"


class ClientError(APIError):
    """4xx client errors (400, 401, 403, 404, 422, 429, etc.)"""
    pass


class ServerError(APIError):
    """5xx server errors (500, 502, 503, 504, etc.)"""
    pass


# Backwards compatibility alias
HTTPException = APIError
```

**Key Design Decisions**:

- Store full response body (don't truncate) - allows debugging large responses
- Truncate only in `__str__` for readable error messages
- Keyword-only arguments maintain backwards compatibility with `APIError(status_code, message)`
- Use `str(error_model)` for error message - let model define its representation

### 2. Response Wrapper

DetailedResponse provides access to HTTP metadata for successful responses:

```python
from typing import Generic, TypeVar, Dict, Optional, Callable, Any
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')


class DetailedResponse(Generic[T]):
    """
    Response wrapper for successful responses with metadata access.

    Only used for 2xx responses - errors always raise exceptions.

    Attributes:
        data: Parsed response model
        status_code: HTTP status code
        headers: Response headers dictionary
        request_id: Request/correlation ID (extracted from headers)
    """

    def __init__(
        self,
        data: T,
        status_code: int,
        headers: Dict[str, str],
        request_id: Optional[str] = None,
    ):
        self.data = data
        self.status_code = status_code
        self.headers = headers
        self.request_id = request_id
        self._handlers: Dict[int, Callable[[T], Any]] = {}
        self._default_handler: Optional[Callable[[T], Any]] = None

    def on(self, status_code: int, handler: Callable[[T], R]) -> 'DetailedResponse[T]':
        """
        Register handler for specific status code (fluent API).

        Example:
            result = (response
                .on(200, lambda data: f"Found: {data.id}")
                .on(201, lambda data: f"Created: {data.id}")
                .otherwise(lambda data: f"Other: {data}")
                .resolve())

        Returns:
            self (for method chaining)
        """
        self._handlers[status_code] = handler
        return self

    def otherwise(self, handler: Callable[[T], R]) -> 'DetailedResponse[T]':
        """
        Register default handler (fluent API).

        Returns:
            self (for method chaining)
        """
        self._default_handler = handler
        return self

    def resolve(self) -> Any:
        """
        Execute the matching handler.

        Raises:
            ValueError: If no handler matches and no default provided

        Returns:
            Result from the matched handler
        """
        if self.status_code in self._handlers:
            return self._handlers[self.status_code](self.data)
        elif self._default_handler:
            return self._default_handler(self.data)
        else:
            raise ValueError(
                f"No handler registered for status {self.status_code} "
                f"and no default handler provided"
            )
```

**Key Features**:

- Generic type parameter maintains type safety
- Fluent API (`on().otherwise().resolve()`) for pattern matching
- Only created for successful responses (errors are exceptions)

### 3. Utility Functions

Helper functions for working with responses and errors:

#### Response Utilities

```python
def unwrap(response: DetailedResponse[T]) -> T:
    """
    Extract data from DetailedResponse.

    Use when you don't need metadata, just the model.

    Example:
        user = unwrap(await get_user_detailed(user_id=123))
    """
    return response.data


def expect(
    response: DetailedResponse,
    status_code: int,
    model_type: Type[T],
) -> T:
    """
    Assert expected status code and narrow type.

    Raises:
        UnexpectedStatusError: If status doesn't match
        TypeError: If model type doesn't match

    Example:
        created = expect(
            await create_user_detailed(data=req),
            201,
            User
        )
    """
    if response.status_code != status_code:
        raise UnexpectedStatusError(
            f"Expected status {status_code}, got {response.status_code}",
            response=response,
        )

    if not isinstance(response.data, model_type):
        raise TypeError(
            f"Expected {model_type.__name__}, "
            f"got {type(response.data).__name__}"
        )

    return response.data


def match(
    response: DetailedResponse[T],
    handlers: Dict[int, Callable[[Any], R]],
    default: Optional[Callable[[DetailedResponse[T]], R]] = None,
) -> R:
    """
    Pattern match on status code.

    Example:
        result = match(
            response,
            {
                200: lambda data: f"Exists: {data.id}",
                201: lambda data: f"Created: {data.id}",
            },
            default=lambda r: f"Unexpected {r.status_code}"
        )
    """
    if response.status_code in handlers:
        return handlers[response.status_code](response.data)
    elif default:
        return default(response)
    else:
        raise ValueError(
            f"No handler for status {response.status_code}"
        )


class UnexpectedStatusError(Exception):
    """Raised when response status doesn't match expectation."""
    def __init__(self, message: str, response: DetailedResponse):
        super().__init__(message)
        self.response = response
```

#### Error Utilities

```python
def has_error_model(
    error: APIError,
    model_type: Type[T]
) -> TypeGuard[APIError]:
    """
    Type guard for checking error model type.

    Example:
        try:
            user = await get_user(123)
        except ClientError as e:
            if has_error_model(e, ValidationError):
                # Type checker knows e.error_model is ValidationError
                for err in e.error_model.errors:
                    print(f"{err.field}: {err.error}")
    """
    return isinstance(error.error_model, model_type)


def get_validation_errors(error: APIError) -> Optional[List[Dict]]:
    """
    Extract validation errors from common error model field names.

    Tries: errors, validation_errors, details
    """
    if not error.error_model:
        return None

    for field in ['errors', 'validation_errors', 'details']:
        if hasattr(error.error_model, field):
            return getattr(error.error_model, field)

    return None


def get_error_code(error: APIError) -> Optional[str]:
    """
    Extract error code from common error model field names.

    Tries: code, error_code, type
    """
    if not error.error_model:
        return None

    for field in ['code', 'error_code', 'type']:
        if hasattr(error.error_model, field):
            return getattr(error.error_model, field)

    return None
```

---

## API Patterns

The generator creates two API variants for each operation, adapting to the operation's response schema.

### Pattern 1: Single Success Response

**When**: Operation has one success status code (most common - ~90% of operations)

**OpenAPI Spec**:

```yaml
/users/{id}:
  get:
    responses:
      "200":
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/User"
      "404":
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ErrorResponse"
```

**Generated Simple API**:

```python
async def get_user(user_id: int) -> User:
    """
    Get user by ID.

    Returns:
        User model (200)

    Raises:
        ClientError: 404 (user not found), 422 (validation error)
        ServerError: 5xx errors

    Error Models:
        404: ErrorResponse
        422: ValidationError
    """
    response = await client.get(f'/users/{user_id}')

    if response.status_code != 200:
        raise _create_error_from_response(
            response, 'GET', f'/users/{user_id}',
            [200], _get_user_error_models
        )

    return User.model_validate_json(response.text)
```

**Generated Detailed API**:

```python
async def get_user_detailed(user_id: int) -> DetailedResponse[User]:
    """
    Get user by ID (with response metadata).

    Returns:
        DetailedResponse[User] with status_code, headers, request_id

    Raises:
        ClientError: 404, 422, etc.
        ServerError: 5xx errors
    """
    response = await client.get(f'/users/{user_id}')

    if response.status_code != 200:
        raise _create_error_from_response(
            response, 'GET', f'/users/{user_id}',
            [200], _get_user_error_models
        )

    return DetailedResponse(
        data=User.model_validate_json(response.text),
        status_code=200,
        headers=dict(response.headers),
        request_id=response.headers.get('x-request-id'),
    )
```

### Pattern 2: Multiple Success Codes, Same Model

**When**: Operation has multiple success codes returning same model (~8% of operations)

**OpenAPI Spec**:

```yaml
/users:
  post:
    responses:
      "200": # User already exists
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/User"
      "201": # User created
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/User"
```

**Generated Simple API**:

```python
async def create_user(data: CreateUserRequest) -> User:
    """
    Create user (idempotent).

    Returns:
        User model (200 if exists, 201 if created)

    Note:
        Multiple success status codes are accepted: [200, 201]
        All return the same User model.
    """
    response = await client.post('/users', json=data.dict())

    # Accept both 200 and 201
    if response.status_code not in [200, 201]:
        raise _create_error_from_response(
            response, 'POST', '/users',
            [200, 201], _create_user_error_models
        )

    return User.model_validate_json(response.text)
```

**Generated Detailed API**:

```python
async def create_user_detailed(data: CreateUserRequest) -> DetailedResponse[User]:
    """
    Create user (with metadata to distinguish created vs existing).

    Returns:
        DetailedResponse[User] where:
        - status_code=200: User already existed
        - status_code=201: User was created

    Example:
        response = await create_user_detailed(data=req)
        if response.status_code == 201:
            print("User was created")
        elif response.status_code == 200:
            print("User already exists")
    """
    response = await client.post('/users', json=data.dict())

    if response.status_code not in [200, 201]:
        raise _create_error_from_response(
            response, 'POST', '/users',
            [200, 201], _create_user_error_models
        )

    return DetailedResponse(
        data=User.model_validate_json(response.text),
        status_code=response.status_code,  # User can check this!
        headers=dict(response.headers),
        request_id=response.headers.get('x-request-id'),
    )
```

### Pattern 3: Multiple Success Codes, Different Models

**When**: Operation has multiple success codes with different models (rare - ~2%)

**OpenAPI Spec**:

```yaml
/resources/{id}:
  post:
    responses:
      "200":
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExistingResource"
      "201":
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreatedResource"
```

**Generated Simple API**:

```python
async def create_resource(resource_id: str) -> ExistingResource:
    """
    Create or get resource.

    Returns:
        ExistingResource model (primary response model)

    Note:
        This operation returns different models for different status codes:
        - 200: ExistingResource
        - 201: CreatedResource

        The simple API always parses to ExistingResource (first defined).
        Use create_resource_detailed() for full type control.
    """
    response = await client.post(f'/resources/{resource_id}')

    if response.status_code not in [200, 201]:
        raise _create_error_from_response(
            response, 'POST', f'/resources/{resource_id}',
            [200, 201], _create_resource_error_models
        )

    # Always parse to first model
    return ExistingResource.model_validate_json(response.text)
```

**Generated Detailed API**:

```python
async def create_resource_detailed(
    resource_id: str
) -> DetailedResponse[ExistingResource | CreatedResource]:
    """
    Create or get resource (with full response control).

    Returns:
        DetailedResponse with Union type:
        - status_code=200: data is ExistingResource
        - status_code=201: data is CreatedResource

    Example:
        response = await create_resource_detailed(resource_id="abc")

        # Pattern 1: Manual type narrowing
        if response.status_code == 200:
            existing: ExistingResource = response.data
            print(existing.existing_field)
        elif response.status_code == 201:
            created: CreatedResource = response.data
            print(created.created_field)

        # Pattern 2: Using type guards
        if is_existing_resource(response.data, response.status_code):
            print(response.data.existing_field)  # Type safe!

        # Pattern 3: Using fluent API
        result = (response
            .on(200, lambda d: f"Existing: {d.existing_field}")
            .on(201, lambda d: f"Created: {d.created_field}")
            .resolve())
    """
    response = await client.post(f'/resources/{resource_id}')

    if response.status_code not in [200, 201]:
        raise _create_error_from_response(
            response, 'POST', f'/resources/{resource_id}',
            [200, 201], _create_resource_error_models
        )

    # Parse based on actual status code
    if response.status_code == 200:
        data = ExistingResource.model_validate_json(response.text)
    elif response.status_code == 201:
        data = CreatedResource.model_validate_json(response.text)
    else:
        # Unreachable, but satisfies type checker
        raise RuntimeError(f"Unexpected status: {response.status_code}")

    return DetailedResponse(
        data=data,
        status_code=response.status_code,
        headers=dict(response.headers),
        request_id=response.headers.get('x-request-id'),
    )
```

**Generated Type Guards** (for Union responses):

```python
def is_existing_resource(
    data: ExistingResource | CreatedResource,
    status_code: int
) -> TypeGuard[ExistingResource]:
    """Type guard for ExistingResource (status 200)."""
    return status_code == 200


def is_created_resource(
    data: ExistingResource | CreatedResource,
    status_code: int
) -> TypeGuard[CreatedResource]:
    """Type guard for CreatedResource (status 201)."""
    return status_code == 201
```

---

## Error Model Parsing

### Response Metadata Structure

Each operation has a metadata dictionary mapping status codes to error model names:

```python
# Simplified structure - just map status codes to model names
_get_user_error_models = {
    '404': 'ErrorResponse',
    '422': 'ValidationError',
    '500': 'ErrorResponse',
}

# Model lookup dictionary (generated per service file)
_ERROR_MODELS = {
    'ErrorResponse': ErrorResponse,
    'ValidationError': ValidationError,
}
```

**Design Rationale**: Use simplified structure instead of full OpenAPI schema - we only need to know which model to parse for each status code.

### Error Creation Function

Single consolidated function handles error creation with model parsing:

```python
def _create_error_from_response(
    response,
    method: str,
    url: str,
    expected_statuses: List[int],
    error_models: Dict[str, str],
) -> APIError:
    """
    Create exception from error response with parsed model.

    Handles:
    - Exact status codes ('404')
    - Wildcard patterns ('4XX', '5XX')
    - Default fallback ('default')
    - Error model parsing with graceful fallback

    Args:
        response: HTTP response object (client-specific)
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        expected_statuses: List of expected success codes
        error_models: Dict mapping status codes to model names

    Returns:
        ClientError or ServerError with full context
    """
    status_code = response.status_code
    headers = dict(response.headers)

    # Extract request ID from common header names
    request_id = (
        headers.get('x-request-id')
        or headers.get('x-correlation-id')
        or headers.get('request-id')
    )

    # Get full response body
    try:
        body_text = response.text
    except (AttributeError, UnicodeDecodeError):
        # Response object doesn't have .text or body contains invalid UTF-8
        body_text = None

    # Determine which error model to use
    status_key = str(status_code)
    model_name = None

    # Try exact match first
    if status_key in error_models:
        model_name = error_models[status_key]
    # Try wildcard patterns
    elif status_code >= 500 and '5XX' in error_models:
        model_name = error_models['5XX']
    elif status_code >= 400 and '4XX' in error_models:
        model_name = error_models['4XX']
    # Try default fallback
    elif 'default' in error_models:
        model_name = error_models['default']

    # Try to parse error model
    error_model = None
    if model_name and model_name in _ERROR_MODELS:
        try:
            model_class = _ERROR_MODELS[model_name]
            error_model = model_class.model_validate_json(body_text)
        except (ValidationError, ValueError, TypeError, JSONDecodeError):
            # Parsing failed - invalid JSON, schema mismatch, wrong type, etc.
            # Keep error_model as None, use raw body instead
            pass

    # Build error message
    message = f"{method} {url} failed with status {status_code}"
    if expected_statuses:
        message += f" (expected {expected_statuses})"

    # Add error message from parsed model
    if error_model:
        message += f": {str(error_model)}"

    # Choose exception class based on status code
    # Defensive: status_code should always be in 4xx or 5xx range at this point
    # due to earlier validation, but we handle edge cases gracefully
    if status_code >= 500:
        exception_class = ServerError
    elif status_code >= 400:
        exception_class = ClientError
    else:
        # Fallback for unexpected status codes (e.g., 3xx, 1xx)
        exception_class = APIError

    return exception_class(
        status_code=status_code,
        message=message,
        method=method,
        url=url,
        request_id=request_id,
        response_headers=headers,
        response_body=body_text,
        error_model=error_model,
    )
```

### HTTP Client Compatibility

Each template generates a client-specific version:

**httpx/requests** (sync access):

```python
def _create_error_from_response(response, method, url, expected_statuses, error_models):
    status_code = response.status_code  # Both use .status_code
    body_text = response.text  # Sync access
    # ... rest of logic
```

**aiohttp** (async access):

```python
async def _create_error_from_response_async(response, method, url, expected_statuses, error_models):
    status_code = response.status  # aiohttp uses .status (not .status_code)
    body_text = await response.text()  # Must await
    # ... rest of logic
```

---

## Code Generation

### service_generator.py Changes

#### New Helper Functions

```python
def _collect_success_codes(operation: Operation) -> List[int]:
    """
    Collect all 2xx status codes from operation responses.

    Handles:
    - Explicit codes: '200', '201', '204'
    - Wildcards: '2XX' expands to range(200, 300)
    - Default: [200] if none defined

    Returns:
        List of success status codes
    """
    codes = []
    has_2xx_wildcard = False

    if operation.responses:
        for status_code in operation.responses.keys():
            if status_code.startswith('2') and status_code.isdigit():
                codes.append(int(status_code))
            elif status_code == '2XX':
                has_2xx_wildcard = True

    if has_2xx_wildcard:
        return list(range(200, 300))
    elif codes:
        return codes
    else:
        return [200]


def _collect_error_models(operation: Operation) -> Dict[str, str]:
    """
    Extract error model names from non-2xx responses.

    Returns:
        Dict mapping status codes to model names
        Example: {'404': 'ErrorResponse', '422': 'ValidationError'}
    """
    error_models = {}

    if not operation.responses:
        return error_models

    for status_code, response_obj in operation.responses.items():
        # Skip success codes
        if status_code.startswith('2'):
            continue

        # Extract model name from $ref
        if isinstance(response_obj, (Response30, Response31)):
            if hasattr(response_obj, 'content') and response_obj.content:
                json_content = response_obj.content.get('application/json')
                if json_content and hasattr(json_content, 'media_type_schema'):
                    schema = json_content.media_type_schema
                    if isinstance(schema, (Reference30, Reference31)):
                        # Extract: #/components/schemas/ErrorResponse → ErrorResponse
                        model_name = schema.ref.split('/')[-1]
                        error_models[status_code] = model_name

    return error_models


def _collect_response_models(operation: Operation) -> Dict[int, str]:
    """
    Extract success response models.

    Returns:
        Dict mapping status codes to model names
        Example: {200: 'User', 201: 'CreatedUser'}
    """
    response_models = {}

    if not operation.responses:
        return response_models

    for status_code, response_obj in operation.responses.items():
        # Only 2xx codes
        if not status_code.startswith('2') or not status_code.isdigit():
            continue

        code = int(status_code)

        # Extract model name
        if isinstance(response_obj, (Response30, Response31)):
            if hasattr(response_obj, 'content') and response_obj.content:
                json_content = response_obj.content.get('application/json')
                if json_content and hasattr(json_content, 'media_type_schema'):
                    schema = json_content.media_type_schema
                    if isinstance(schema, (Reference30, Reference31)):
                        model_name = schema.ref.split('/')[-1]
                        response_models[code] = model_name

    return response_models
```

#### Updated OpReturnType Model

```python
class OpReturnType(BaseModel):
    type: Optional[TypeConversion] = None
    status_code: int  # Primary/first success code
    success_codes: List[int] = []  # All success codes
    has_wildcard_success: bool = False  # True if spec uses '2XX' wildcard pattern
    response_models: Dict[int, str] = {}  # {200: 'User', 201: 'CreatedUser'}
    error_models: Dict[str, str] = {}  # {'404': 'ErrorResponse'}
    complex_type: bool = False
    list_type: Optional[str] = None
```

**Field Descriptions**:

- `has_wildcard_success`: Set to `True` when the OpenAPI spec defines `'2XX'` wildcard in responses section, indicating any 2xx status code should be accepted as success. When `True`, generated code uses range check `(200 <= status < 300)` instead of explicit list check.

### Template Structure

**service.jinja2**:

```jinja2
{# Imports #}
from typing import Any, Dict, List, Optional
{% if use_orjson %}
import orjson
{% endif %}
import {{ library_import }}

from ..api_config import APIConfig
from ..errors import APIError, ClientError, ServerError
from ..response import DetailedResponse

{# Import error models (only non-2xx models) #}
{% for model_name in error_model_names %}
from ..models.{{ model_name }} import {{ model_name }}
{% endfor %}

{# Model lookup dictionary #}
_ERROR_MODELS = {
{% for model_name in error_model_names %}
    '{{ model_name }}': {{ model_name }},
{% endfor %}
}

{# Per-operation error models #}
{% for operation in operations %}
_{{ operation.operation_id }}_error_models = {{ operation.error_models | tojson }}

{% endfor %}

{# Error creation function (client-specific) #}
{% if library == 'aiohttp' %}
async def _create_error_from_response_async(...):
    # Async version for aiohttp
    ...
{% else %}
def _create_error_from_response(...):
    # Sync version for httpx/requests
    ...
{% endif %}

{# Generated operations #}
{% for operation in operations %}

{# Simple API #}
{% if async_client %}async {% endif %}def {{ operation.operation_id }}(
    {% if operation.params %}{{ operation.params }}{% endif %}
) -> {{ operation.return_type }}:
    """{{ operation.docstring }}"""
    # ... implementation

    # Check success
    {% if operation.has_wildcard_success %}
    # OpenAPI spec uses '2XX' wildcard - accept any 2xx status code
    if not (200 <= response.status_code < 300):
    {% else %}
    # OpenAPI spec defines explicit success codes
    if response.status_code not in {{ operation.success_codes }}:
    {% endif %}
        raise _create_error_from_response(...)

    return {{ operation.parse_response }}


{# Detailed API #}
{% if async_client %}async {% endif %}def {{ operation.operation_id }}_detailed(
    {% if operation.params %}{{ operation.params }}{% endif %}
) -> DetailedResponse[{{ operation.detailed_return_type }}]:
    """{{ operation.detailed_docstring }}"""
    # ... implementation

    if response.status_code not in {{ operation.success_codes }}:
        raise _create_error_from_response(...)

    {% if operation.has_union_response %}
    # Parse based on status code
    {% for status_code, model in operation.response_models.items() %}
    {% if loop.first %}if{% else %}elif{% endif %} response.status_code == {{ status_code }}:
        data = {{ model }}.model_validate_json(response.text)
    {% endfor %}
    {% else %}
    # Single model
    data = {{ operation.return_type }}.model_validate_json(response.text)
    {% endif %}

    return DetailedResponse(
        data=data,
        status_code=response.status_code,
        headers=dict(response.headers),
        request_id=response.headers.get('x-request-id'),
    )

{% if operation.has_union_response %}
{# Type guards for Union responses #}
{% for status_code, model in operation.response_models.items() %}
def is_{{ model|lower }}(
    data: {{ operation.union_type }},
    status_code: int
) -> TypeGuard[{{ model }}]:
    """Type guard for {{ model }} (status {{ status_code }})."""
    return status_code == {{ status_code }}

{% endfor %}
{% endif %}

{% endfor %}
```

---

## Usage Examples

### Example 1: Simple API - Basic Usage

```python
from client.services.user_service import get_user
from client.errors import ClientError

# Success case
user = await get_user(user_id=123)
print(f"User: {user.name}")

# Error handling
try:
    user = await get_user(user_id=999)
except ClientError as e:
    print(f"Error {e.status_code}: {e.message}")
    print(f"Request ID: {e.request_id}")
```

### Example 2: Structured Error Handling

```python
from client.services.user_service import create_user
from client.models import CreateUserRequest, ValidationError
from client.errors import ClientError
from client.utils import has_error_model

try:
    user = await create_user(
        data=CreateUserRequest(email="invalid", name="Test")
    )
except ClientError as e:
    if e.status_code == 422 and has_error_model(e, ValidationError):
        # Type-safe access to ValidationError fields
        validation_error: ValidationError = e.error_model
        print(f"Validation failed: {validation_error.message}")
        for field_error in validation_error.errors:
            print(f"  {field_error.field}: {field_error.error}")
    elif e.status_code == 409:
        print("User already exists")
    else:
        print(f"Unexpected error: {e}")
```

### Example 3: Detailed API - Metadata Access

```python
from client.services.user_service import get_user_detailed
from client.utils import unwrap

# Access metadata
response = await get_user_detailed(user_id=123)
print(f"User: {response.data.name}")
print(f"Status: {response.status_code}")
print(f"Request ID: {response.request_id}")
print(f"Cache-Control: {response.headers.get('cache-control')}")

# Or just unwrap if you don't need metadata
user = unwrap(await get_user_detailed(user_id=123))
```

### Example 4: Multiple Success Codes

```python
from client.services.user_service import create_user_detailed

response = await create_user_detailed(data=req)

# Check which status was returned
if response.status_code == 201:
    print("User was created")
elif response.status_code == 200:
    print("User already exists")

user = response.data  # Same model either way
```

### Example 5: Union Response with Type Guards

```python
from client.services.resource_service import (
    create_resource_detailed,
    is_existing_resource,
    is_created_resource
)

response = await create_resource_detailed(resource_id="abc")

# Pattern 1: Type guards
if is_existing_resource(response.data, response.status_code):
    # Type narrowed to ExistingResource
    print(f"Existing: {response.data.existing_field}")
elif is_created_resource(response.data, response.status_code):
    # Type narrowed to CreatedResource
    print(f"Created: {response.data.created_field}")
```

### Example 6: Union Response with Fluent API

```python
from client.services.resource_service import create_resource_detailed

response = await create_resource_detailed(resource_id="abc")

# Fluent pattern matching
result = (response
    .on(200, lambda data: f"Found existing: {data.existing_field}")
    .on(201, lambda data: f"Created new: {data.created_field}")
    .otherwise(lambda data: f"Unexpected: {data}")
    .resolve())

print(result)
```

### Example 7: Using expect() Utility

```python
from client.services.user_service import create_user_detailed
from client.utils import expect
from client.models import User

# Assert specific status code
created_user = expect(
    await create_user_detailed(data=req),
    201,  # Expect 201 Created
    User
)
# Raises UnexpectedStatusError if not 201
print(f"Created: {created_user.name}")
```

### Example 8: Using match() Utility

```python
from client.services.resource_service import create_resource_detailed
from client.utils import match

response = await create_resource_detailed(resource_id="abc")

result = match(
    response,
    {
        200: lambda data: handle_existing(data),
        201: lambda data: handle_created(data),
    },
    default=lambda r: f"Unexpected status {r.status_code}"
)
```

---

## Implementation Plan

### Phase 1: Core Exceptions (Week 1)

- [ ] Create `errors.py` module
- [ ] Implement `APIError`, `ClientError`, `ServerError`
- [ ] Add `HTTPException` alias
- [ ] Write unit tests for exception creation
- [ ] Test `__str__` formatting with/without metadata

### Phase 2: Response Wrapper (Week 1)

- [ ] Create `response.py` module
- [ ] Implement `DetailedResponse[T]` generic class
- [ ] Add fluent API methods (`on()`, `otherwise()`, `resolve()`)
- [ ] Write unit tests for response wrapper
- [ ] Test with various model types

### Phase 3: Utility Functions (Week 2)

- [ ] Implement `unwrap()`
- [ ] Implement `expect()` with `UnexpectedStatusError`
- [ ] Implement `match()`
- [ ] Implement error utilities (`has_error_model()`, etc.)
- [ ] Write comprehensive utility tests
- [ ] Document utility functions

### Phase 4: Service Generator Updates (Week 2-3)

- [ ] Implement `_collect_success_codes()`
- [ ] Implement `_collect_error_models()`
- [ ] Implement `_collect_response_models()`
- [ ] Update `OpReturnType` model with new fields
- [ ] Add tests for collection functions

### Phase 5: Error Creation Functions (Week 3)

- [ ] Implement `_create_error_from_response()` for httpx/requests
- [ ] Implement `_create_error_from_response_async()` for aiohttp
- [ ] Handle wildcard patterns ('2XX', '4XX', '5XX', 'default')
- [ ] Implement error model parsing with fallback
- [ ] Test with various error responses
- [ ] Test all three HTTP clients

### Phase 6: Simple API Generation (Week 4)

- [ ] Update templates to generate simple API functions
- [ ] Handle single success code case
- [ ] Handle multiple same-model codes
- [ ] Handle multiple different-model codes (picks first)
- [ ] Generate docstrings with error documentation
- [ ] Add integration tests

### Phase 7: Detailed API Generation (Week 4-5)

- [ ] Generate `_detailed()` function variants
- [ ] Handle same-model responses (direct type)
- [ ] Handle different-model responses (Union type)
- [ ] Implement status-based parsing for Union types
- [ ] Generate comprehensive docstrings with examples
- [ ] Add integration tests

### Phase 8: Type Guards (Week 5)

- [ ] Generate type guard functions for Union responses
- [ ] Test type narrowing behavior
- [ ] Verify type checker integration (mypy/pyright)

### Phase 9: Integration Testing (Week 6)

- [ ] Test with real OpenAPI specs (petstore, etc.)
- [ ] Test single success code operations
- [ ] Test multiple same-model codes
- [ ] Test multiple different-model codes
- [ ] Test wildcard patterns ('2XX', etc.)
- [ ] Test error model parsing
- [ ] Test unparseable error bodies
- [ ] Test all three HTTP clients (httpx, requests, aiohttp)
- [ ] Test backwards compatibility with existing code

### Phase 10: Documentation (Week 6)

- [ ] Update README with new error handling features
- [ ] Document simple vs detailed API
- [ ] Add usage examples to docs
- [ ] Document utility functions
- [ ] Create migration guide
- [ ] Document limitations and edge cases

---

## Appendices

### Appendix A: Design Rationale

#### Why Two APIs (Simple + Detailed)?

**Simple API** serves 90%+ of use cases:

- Direct model returns are ergonomic
- Most operations don't need response metadata
- Exception-based error handling is intuitive

**Detailed API** handles edge cases:

- Need response headers (pagination, caching)
- Need request IDs for logging
- Multiple models per operation
- Status code discrimination

#### Why Minimal Exception Hierarchy?

Flat hierarchy (3 types) avoids naming conflicts:

- OpenAPI specs may define `ValidationError`, `NotFoundError` models
- Checking `e.status_code` is clearer than many exception types
- Simple to understand and use

#### Why Store Full Response Body?

Debugging requires complete error information:

- API might return large error details
- Truncation loses critical debugging info
- User can access full body if needed
- Only truncate in `__str__` for display

#### Why Use str(error_model) for Messages?

Let models define their representation:

- More flexible than field sniffing
- Models can implement custom `__str__`
- Works with any error model structure
- Simpler implementation

### Appendix B: OpenAPI Spec Support

#### Supported Features

✅ Multiple explicit success codes (200, 201, 204)
✅ Wildcard patterns (2XX, 4XX, 5XX)
✅ Default responses
✅ Error response schemas ($ref to components)
✅ Multiple content types (prefers application/json)
✅ Request/correlation ID headers

#### Not Supported (Future Enhancements)

❌ Streaming responses
❌ Non-JSON error responses (text/plain, XML)
❌ Response-level $ref (only schema-level)
❌ Inline error schemas without $ref

### Appendix C: Backwards Compatibility

#### Constructor Compatibility

Old code works unchanged:

```python
# Old style still works
raise HTTPException(404, "Not found")

# New style with rich context
raise APIError(
    status_code=404,
    message="Not found",
    method="GET",
    url="/users/123",
    # ...
)
```

#### Exception Catching

All existing exception handlers continue to work:

```python
# Still works
try:
    user = get_user(123)
except HTTPException as e:
    print(f"Error {e.status_code}: {e.message}")
```

#### Migration Path

Users can adopt features incrementally:

1. No changes required (backwards compatible)
2. Access new attributes (`request_id`, `error_model`)
3. Use new exception types (`ClientError`, `ServerError`)
4. Adopt detailed API for specific operations
5. Use utility functions (`unwrap`, `expect`, etc.)

### Appendix D: Performance Considerations

#### Error Model Parsing Overhead

- Parsing only occurs on errors (not hot path)
- Graceful fallback if parsing fails
- No overhead for successful requests

#### Response Wrapper Overhead

- Minimal (just attribute storage)
- Simple API has zero overhead
- Detailed API only used when needed

#### Type Guard Performance

- Type guards are runtime checks (no overhead in production)
- Used for type narrowing only
- No performance impact

---

## References

- Issue #100: https://github.com/MarcoMuellner/openapi-python-generator/issues/100
- OpenAPI 3.0 Spec: https://spec.openapis.org/oas/v3.0.3
- OpenAPI 3.1 Spec: https://spec.openapis.org/oas/v3.1.0
- Python TypeGuard: https://peps.python.org/pep-0647/
