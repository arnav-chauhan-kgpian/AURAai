# API reference

All routes are mounted under the configured prefix (`API_V1_PREFIX`, default
`/api/v1`). Interactive documentation is served at `/docs` (Swagger) and
`/redoc` when the backend is running.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness probe. |
| `POST` | `/skin/analyze` | Run skin analysis for an image and return scored concerns. |
| `POST` | `/vto/render` | Render a garment on a person image. |
| `POST` | `/uploads/image` | Validate and persist an uploaded image (multipart). |
| `POST` | `/chat` | Run one turn of the autonomous stylist agent. |

## Error contract

Errors are returned with the appropriate HTTP status and a consistent body:

```json
{
  "error": {
    "code": "skin_analysis_error",
    "message": "Human-readable description"
  }
}
```

Error codes are defined by the exception hierarchy in
`backend/app/core/exceptions.py`.

## Correlation

Every request is tagged with an `X-Request-ID` header (echoed back on the
response) and bound into structured logs for traceability.
