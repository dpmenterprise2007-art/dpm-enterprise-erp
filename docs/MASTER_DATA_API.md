# Master Data API

Initial endpoints:
- POST /api/v1/customers
- GET /api/v1/customers?search=&active_only=true
- GET /api/v1/customers/{uuid}
- PATCH /api/v1/customers/{uuid}
- DELETE /api/v1/customers/{uuid} (deactivates; does not erase)
- POST /api/v1/vendors
- GET /api/v1/vendors?search=
- POST /api/v1/items
- GET /api/v1/items?search=

OpenAPI documentation is available at /docs when the API is running.

## Development status
This is a development-stage master-data API. Authentication, authorization, database migrations, audit-event recording, pagination, and production-grade GSTIN verification are not yet implemented. Do not expose this API to the public internet or enter live customer data until those controls are complete.
