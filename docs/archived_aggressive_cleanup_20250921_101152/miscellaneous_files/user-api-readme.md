**Status**: 🔒 **LOCKED** - SSOT Document
**Version**: 1.0
**Last Updated**: 2025-01-17
**Source**: Consolidated from original documentation

---

# User Api API

## Overview

This API provides endpoints for user api management.

## Endpoints

### GET /user_api/

Retrieve all user api data.

**Response:**

```json
{
  "message": "Success message",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": []
}
```

### POST /user_api/

Create new user api.

**Request Body:**

```json
{
  "name": "string",
  "value": "string"
}
```

**Response:**

```json
{
  "message": "Success message",
  "timestamp": "2025-01-15T10:30:00Z",
  "id": "generated_id"
}
```

### PUT /user_api/{item_id}

Update user api by ID.

### DELETE /user_api/{item_id}

Delete user api by ID.

## Created

2025-09-17 21:48:38
