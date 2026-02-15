"""Unit tests for error handler middleware."""

import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware.error_handler import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


def make_request():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "query_string": b"",
        "headers": [],
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_http_exception_handler_with_dict_detail():
    request = make_request()
    exc = StarletteHTTPException(
        status_code=404,
        detail={"detail": "Not found", "code": "not_found"},
    )
    response = await http_exception_handler(request, exc)
    assert response.status_code == 404
    import json
    body = json.loads(response.body)
    assert body["detail"] == "Not found"
    assert body["code"] == "not_found"


@pytest.mark.asyncio
async def test_http_exception_handler_with_string_detail():
    request = make_request()
    exc = StarletteHTTPException(status_code=403, detail="Forbidden")
    response = await http_exception_handler(request, exc)
    assert response.status_code == 403
    import json
    body = json.loads(response.body)
    assert body["detail"] == "Forbidden"
    assert body["code"] == "http_error"


@pytest.mark.asyncio
async def test_validation_exception_handler():
    request = make_request()
    # Create a simple validation error
    from pydantic import BaseModel, ValidationError

    class M(BaseModel):
        x: int

    try:
        M(x="not_an_int")
    except ValidationError as e:
        rve = RequestValidationError(errors=e.errors())

    response = await validation_exception_handler(request, rve)
    assert response.status_code == 422
    import json
    body = json.loads(response.body)
    assert body["code"] == "validation_error"
    assert "errors" in body


@pytest.mark.asyncio
async def test_generic_exception_handler():
    request = make_request()
    exc = RuntimeError("Something went wrong")
    response = await generic_exception_handler(request, exc)
    assert response.status_code == 500
    import json
    body = json.loads(response.body)
    assert body["code"] == "internal_error"
    assert body["detail"] == "Internal server error"
