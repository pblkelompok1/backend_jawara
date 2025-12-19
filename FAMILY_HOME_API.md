# Family & Home API Documentation

**Backend Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (or your deployment URL)  
**Created:** December 19, 2025

---

## Overview

This document describes the newly implemented **Family** and **Home** CRUD endpoints for the neighborhood management system. These APIs allow you to manage family units, their homes, and track movement/occupancy history.

### Key Concepts

- **Family (Keluarga):** A group of residents living together, identified by a Kartu Keluarga (KK)
- **Home (Rumah):** Physical residence where a family lives
- **RT (Rukun Tetangga):** Neighborhood unit that families belong to
- **Resident (Warga):** Individual people who belong to families

### Relationships

```
RT (1) ──── (many) Family
Family (1) ──── (many) Resident
Family (1) ──── (1) Home (active)
Home (1) ──── (many) HomeHistory
Family (1) ──── (many) FamilyMovement
```

---

## Family API

### 1. List Families

**GET** `/family/`

Get a paginated list of families with optional filters.

**Query Parameters:**
- `rt_id` (integer, optional): Filter by RT ID
- `status` (string, optional): Filter by status (e.g., "active", "inactive")
- `family_name` (string, optional): Filter by family name (case-insensitive partial match)
- `offset` (integer, default: 0): Pagination offset
- `limit` (integer, default: 10): Number of results per page

**Response:**
```json
{
  "total": 50,
  "offset": 0,
  "limit": 10,
  "data": [
    {
      "family_id": "123e4567-e89b-12d3-a456-426614174000",
      "family_name": "Keluarga Budi Santoso",
      "kk_path": "storage/kk/abc123.pdf",
      "status": "active",
      "resident_id": "456e7890-e89b-12d3-a456-426614174111",
      "rt_id": 1,
      "rt_name": "RT 001",
      "head_of_family_name": "Budi Santoso",
      "total_members": 4
    }
  ]
}
```

**Example Request:**
```javascript
fetch('/family/?rt_id=1&status=active&limit=20')
  .then(res => res.json())
  .then(data => console.log(data.data));
```

---

### 2. Get Family by ID

**GET** `/family/{family_id}`

Get detailed information about a specific family.

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Response:**
```json
{
  "family_id": "123e4567-e89b-12d3-a456-426614174000",
  "family_name": "Keluarga Budi Santoso",
  "kk_path": "storage/kk/abc123.pdf",
  "status": "active",
  "resident_id": "456e7890-e89b-12d3-a456-426614174111",
  "rt_id": 1,
  "rt_name": "RT 001",
  "head_of_family_name": "Budi Santoso",
  "total_members": 4
}
```

**Error Responses:**
- `404 Not Found`: Family does not exist

---

### 3. Create Family

**POST** `/family/`

Create a new family record.

**Request Body:**
```json
{
  "family_name": "Keluarga Budi Santoso",
  "kk_path": "storage/kk/temp.pdf",
  "status": "active",
  "resident_id": "456e7890-e89b-12d3-a456-426614174111",
  "rt_id": 1
}
```

**Fields:**
- `family_name` (string, required): Name of the family
- `kk_path` (string, required): Path to Kartu Keluarga document
- `status` (string, optional, default: "active"): Status of the family
- `resident_id` (UUID, optional): ID of the head of family (resident)
- `rt_id` (integer, required): RT (neighborhood) ID

**Response:** `201 Created` with family object

**Validations:**
- RT must exist
- If `resident_id` provided, resident must exist and cannot be head of another active family

**Example Request:**
```javascript
fetch('/family/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    family_name: 'Keluarga Budi',
    kk_path: 'storage/kk/temp.pdf',
    rt_id: 1
  })
})
.then(res => res.json())
.then(data => console.log('Created:', data));
```

---

### 4. Update Family

**PUT** `/family/{family_id}`

Update an existing family record.

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Request Body (all fields optional):**
```json
{
  "family_name": "Keluarga Budi Santoso (Updated)",
  "status": "inactive",
  "resident_id": "789e0123-e89b-12d3-a456-426614174222"
}
```

**Response:** `200 OK` with updated family object

**Validations:**
- Same validations as create
- Cannot assign resident who is already head of another active family

---

### 5. Delete Family

**DELETE** `/family/{family_id}`

Soft delete a family (sets status to "inactive").

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Response:** `204 No Content`

**Validations:**
- Cannot delete family if it has active residents (status "approved")

**Error Responses:**
- `400 Bad Request`: Family has active residents
- `404 Not Found`: Family does not exist

---

### 6. Get Family Residents

**GET** `/family/{family_id}/residents`

Get all residents (members) belonging to a family.

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Response:**
```json
{
  "total": 4,
  "data": [
    {
      "resident_id": "456e7890-e89b-12d3-a456-426614174111",
      "nik": "3201234567890001",
      "name": "Budi Santoso",
      "phone": "081234567890",
      "family_role": "head",
      "gender": "Laki-laki",
      "date_of_birth": "1980-01-15",
      "is_deceased": false,
      "status": "approved"
    },
    {
      "resident_id": "456e7890-e89b-12d3-a456-426614174222",
      "nik": "3201234567890002",
      "name": "Siti Aminah",
      "phone": "081234567891",
      "family_role": "wife",
      "gender": "Perempuan",
      "date_of_birth": "1985-05-20",
      "is_deceased": false,
      "status": "approved"
    }
  ]
}
```

---

### 7. Upload Kartu Keluarga (KK)

**POST** `/family/{family_id}/upload-kk`

Upload or update the family's Kartu Keluarga document.

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Request:** `multipart/form-data`
- `file` (File): KK document (PDF, JPG, JPEG, or PNG)

**Response:**
```json
{
  "message": "KK uploaded successfully",
  "kk_path": "storage/kk/550e8400-e29b-41d4-a716-446655440000.pdf"
}
```

**Validations:**
- File must be PDF, JPG, JPEG, or PNG
- Family must exist

**Example Request:**
```javascript
const formData = new FormData();
formData.append('file', kkFile);

fetch('/family/123e4567-e89b-12d3-a456-426614174000/upload-kk', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log('Uploaded:', data.kk_path));
```

---

### 8. Create Family Movement

**POST** `/family/{family_id}/movements`

Record a family relocation/movement to a new address.

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Request Body:**
```json
{
  "reason": "Pindah karena pekerjaan",
  "old_address": "Jl. Lama No. 123",
  "new_address": "Jl. Baru No. 456"
}
```

**Fields:**
- `reason` (string, required): Reason for moving
- `old_address` (string, required): Previous address
- `new_address` (string, required): New address

**Response:** `201 Created`
```json
{
  "family_movement_id": 1,
  "reason": "Pindah karena pekerjaan",
  "old_address": "Jl. Lama No. 123",
  "new_address": "Jl. Baru No. 456",
  "family_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

### 9. Get Family Movement History

**GET** `/family/{family_id}/movements`

Get all movement/relocation records for a family.

**Path Parameters:**
- `family_id` (UUID): Family identifier

**Response:**
```json
[
  {
    "family_movement_id": 2,
    "reason": "Renovasi rumah",
    "old_address": "Jl. Lama No. 123",
    "new_address": "Jl. Baru No. 456",
    "family_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  {
    "family_movement_id": 1,
    "reason": "Pindah karena pekerjaan",
    "old_address": "Jl. Lama No. 100",
    "new_address": "Jl. Lama No. 123",
    "family_id": "123e4567-e89b-12d3-a456-426614174000"
  }
]
```

---

## Home API

### 1. List Homes

**GET** `/home/`

Get a paginated list of homes with optional filters.

**Query Parameters:**
- `status` (string, optional): Filter by status (e.g., "active", "inactive")
- `home_name` (string, optional): Filter by home name (case-insensitive partial match)
- `family_id` (UUID, optional): Filter by family ID
- `rt_id` (integer, optional): Filter by RT ID (via family)
- `offset` (integer, default: 0): Pagination offset
- `limit` (integer, default: 10): Number of results per page

**Response:**
```json
{
  "total": 30,
  "offset": 0,
  "limit": 10,
  "data": [
    {
      "home_id": 1,
      "home_name": "Rumah Budi",
      "home_address": "Jl. Merdeka No. 45",
      "status": "active",
      "family_id": "123e4567-e89b-12d3-a456-426614174000",
      "family_name": "Keluarga Budi Santoso",
      "rt_name": "RT 001",
      "total_residents": 4
    }
  ]
}
```

**Example Request:**
```javascript
fetch('/home/?status=active&rt_id=1')
  .then(res => res.json())
  .then(data => console.log(data.data));
```

---

### 2. Get Home by ID

**GET** `/home/{home_id}`

Get detailed information about a specific home.

**Path Parameters:**
- `home_id` (integer): Home identifier

**Response:**
```json
{
  "home_id": 1,
  "home_name": "Rumah Budi",
  "home_address": "Jl. Merdeka No. 45",
  "status": "active",
  "family_id": "123e4567-e89b-12d3-a456-426614174000",
  "family_name": "Keluarga Budi Santoso",
  "rt_name": "RT 001",
  "total_residents": 4
}
```

---

### 3. Create Home

**POST** `/home/`

Create a new home record.

**Request Body:**
```json
{
  "home_name": "Rumah Budi",
  "home_address": "Jl. Merdeka No. 45",
  "status": "active",
  "family_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Fields:**
- `home_name` (string, required): Name/identifier of the home
- `home_address` (string, required): Physical address
- `status` (string, optional, default: "active"): Status of the home
- `family_id` (UUID, required): ID of the family occupying this home

**Response:** `201 Created` with home object

**Validations:**
- Family must exist
- Family cannot have more than one active home

**Auto-Generated:**
- Creates a `HomeHistory` entry with `moved_in_date` = today if status is "active"

---

### 4. Update Home

**PUT** `/home/{home_id}`

Update an existing home record.

**Path Parameters:**
- `home_id` (integer): Home identifier

**Request Body (all fields optional):**
```json
{
  "home_name": "Rumah Budi (Renovated)",
  "home_address": "Jl. Merdeka No. 45A",
  "family_id": "789e0123-e89b-12d3-a456-426614174333"
}
```

**Response:** `200 OK` with updated home object

**Auto-Generated:**
- If `family_id` changes, closes old `HomeHistory` and creates new one

---

### 5. Delete Home

**DELETE** `/home/{home_id}`

Soft delete a home (sets status to "inactive").

**Path Parameters:**
- `home_id` (integer): Home identifier

**Response:** `204 No Content`

**Auto-Generated:**
- Closes any open `HomeHistory` entries (sets `moved_out_date` = today)

---

### 6. Get Home History

**GET** `/home/{home_id}/history`

Get the occupancy history of a home (which families lived there and when).

**Path Parameters:**
- `home_id` (integer): Home identifier

**Response:**
```json
[
  {
    "home_id": 1,
    "family_id": "123e4567-e89b-12d3-a456-426614174000",
    "moved_in_date": "2024-01-15",
    "moved_out_date": null,
    "family_name": null
  },
  {
    "home_id": 1,
    "family_id": "789e0123-e89b-12d3-a456-426614174333",
    "moved_in_date": "2023-01-01",
    "moved_out_date": "2024-01-14",
    "family_name": null
  }
]
```

**Note:** Results are ordered by `moved_in_date` descending (most recent first).

---

### 7. Create Home History

**POST** `/home/history`

Manually create a home history record.

**Request Body:**
```json
{
  "home_id": 1,
  "family_id": "123e4567-e89b-12d3-a456-426614174000",
  "moved_in_date": "2024-01-15",
  "moved_out_date": "2024-12-31"
}
```

**Fields:**
- `home_id` (integer, required): Home identifier
- `family_id` (UUID, required): Family identifier
- `moved_in_date` (date, required): Date family moved in (format: "YYYY-MM-DD")
- `moved_out_date` (date, optional): Date family moved out (null if still occupying)

**Response:** `201 Created` with history object

**Note:** This endpoint is for manual record-keeping. History is usually auto-created/updated via home create/update operations.

---

## Common Patterns

### Authentication
All endpoints require authentication. Include your JWT token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

### Error Responses

**400 Bad Request:**
```json
{
  "detail": "Family already has an active home. Please deactivate the existing home first."
}
```

**404 Not Found:**
```json
{
  "detail": "Family not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "family_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Date Format
All dates use ISO 8601 format: `YYYY-MM-DD` (e.g., "2024-12-19")

### UUID Format
All UUIDs are returned as strings in standard format: `"123e4567-e89b-12d3-a456-426614174000"`

---

## Business Rules

### Family Rules
1. **One Head per Family:** A resident can only be head (`resident_id`) of one active family at a time
2. **RT Requirement:** Every family must belong to an RT
3. **Soft Delete:** Deleting a family sets status to "inactive" rather than removing it
4. **Active Residents Check:** Cannot delete a family if it has active (approved) residents

### Home Rules
1. **One Active Home per Family:** A family can only have one home with status "active" at any given time
2. **History Tracking:** Moving a family to a new home automatically closes the old history and creates a new one
3. **Soft Delete:** Deleting a home sets status to "inactive" and closes any open history entries

### File Upload
- **Allowed Formats:** PDF, JPG, JPEG, PNG
- **Storage Location:** `storage/kk/`
- **Filename:** Auto-generated UUID to prevent conflicts

---

## Integration Tips for Frontend

### Fetching Family List with RT Filter
```javascript
async function getFamiliesByRT(rtId) {
  const response = await fetch(`/family/?rt_id=${rtId}&status=active&limit=100`);
  const data = await response.json();
  return data.data; // Array of families
}
```

### Creating Family with KK Upload
```javascript
async function createFamilyWithKK(familyData, kkFile) {
  // Step 1: Create family
  const createResponse = await fetch('/family/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...familyData,
      kk_path: 'storage/kk/temp.pdf' // Temporary path
    })
  });
  const family = await createResponse.json();
  
  // Step 2: Upload KK
  const formData = new FormData();
  formData.append('file', kkFile);
  
  await fetch(`/family/${family.family_id}/upload-kk`, {
    method: 'POST',
    body: formData
  });
  
  return family;
}
```

### Displaying Home with Family Info
```javascript
async function getHomeDetails(homeId) {
  const response = await fetch(`/home/${homeId}`);
  const home = await response.json();
  
  return {
    address: home.home_address,
    familyName: home.family_name,
    rt: home.rt_name,
    occupants: home.total_residents
  };
}
```

---

## Testing Endpoints

### Using cURL

**List families:**
```bash
curl -X GET "http://localhost:8000/family/?rt_id=1&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create home:**
```bash
curl -X POST "http://localhost:8000/home/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "home_name": "Rumah Test",
    "home_address": "Jl. Test No. 1",
    "family_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

**Upload KK:**
```bash
curl -X POST "http://localhost:8000/family/123e4567-e89b-12d3-a456-426614174000/upload-kk" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/kk.pdf"
```

---

## Support & Questions

For questions or issues with these endpoints:
1. Check the error response `detail` field for specific validation messages
2. Verify all required fields are provided
3. Ensure UUIDs are in correct format
4. Check that related entities (RT, Family, Resident) exist before creating references

**Database Schema Reference:** See `alembic/versions/002_create_necessary_tables_related_to_residents.py`  
**Entity Models:** See `src/entities/family.py` and `src/entities/home.py`
