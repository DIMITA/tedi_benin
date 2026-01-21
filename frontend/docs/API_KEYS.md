# API Keys Page Documentation

## Overview

The API Keys page (`ApiKeysView.vue`) allows users to manage authentication credentials for accessing the TEDI API. This page is crucial for developers and organizations who want to programmatically access TEDI's data through the REST API.

**Route**: `/api-keys`

---

## Purpose

The API Keys page serves multiple functions:

1. **Authentication Management**: Create and manage API keys for secure access to TEDI data
2. **Documentation Hub**: Provides quick reference for API usage, endpoints, and rate limits
3. **Security**: Ensures controlled access to data with revocable credentials

---

## Features

### 1. Current API Key Display

- Shows the user's currently active API key in a masked format
- Format: `abc123...xyz789` (first 12 + last 8 characters visible)
- Status indicator (Active/Inactive)

### 2. API Key Creation

Users can create new API keys by providing:
- **Key Name** (required): Descriptive name for the key (e.g., "Production Key", "Development")
- **Owner Name** (required): Full name of the person responsible
- **Owner Email** (required): Contact email for key owner
- **Owner Organization** (optional): Company or organization name

**Important Security Note**: The full API key is only shown once upon creation. Users must save it immediately as it cannot be retrieved later.

### 3. Usage Documentation

The page includes embedded documentation covering:

#### Authentication Method
```bash
curl -H "X-API-KEY: your-api-key-here" \
  https://api.tedi.africa/api/v1/agriculture/communes
```

API keys must be included in the `X-API-KEY` header of all HTTP requests.

#### Rate Limits
- **1,000 requests per hour**
- **10,000 requests per day**

These limits ensure fair usage and system stability.

#### Available Endpoints
Quick reference to key API endpoints:
- `/api/v1/agriculture/communes` - List all communes with geospatial data
- `/api/v1/agriculture/crops` - List all tracked crop types
- `/api/v1/agriculture/index` - Retrieve agricultural statistics with filtering

Full API documentation is linked at the bottom of the page.

---

## Integration with Backend Data Ingestion System

### How API Keys Relate to the Scheduler

The API Keys system integrates with the automated data ingestion scheduler in several ways:

#### 1. **Access to Ingested Data**
- API keys provide authenticated access to data collected by the scheduler
- When the scheduler successfully ingests data from sources like FAOSTAT, World Bank, ILOSTAT, or OpenStreetMap, that data becomes immediately available through the API
- Users with valid API keys can query this freshly ingested data

#### 2. **Data Freshness Tracking**
The backend scheduler (configured in `/backend/app/tasks/scheduler.py`) runs every 6 hours and updates dataset versions. API consumers can:
- Query `/api/v1/data-sources` to see last update timestamps
- Access `/api/v1/dataset-versions` to check data freshness
- Use the API to programmatically monitor when new data becomes available

#### 3. **Data Source Attribution**
Each API response includes metadata about data provenance:
```json
{
  "data": [...],
  "meta": {
    "source": "FAOSTAT",
    "last_updated": "2026-01-13T06:00:00Z",
    "reliability_score": 0.9,
    "version": "auto_20260113_agriculture_production_data"
  }
}
```

This information comes directly from the `DatasetVersion` and `IngestionLog` tables managed by the scheduler.

#### 4. **External Source API Keys vs. TEDI API Keys**
**Important Distinction**:
- **TEDI API Keys** (managed on this page): Used by clients to access TEDI's aggregated data
- **External Source API Keys** (configured in backend): Used by the scheduler to fetch data from sources like World Bank API, ILOSTAT, etc.

These are separate. End users don't need World Bank API keys; they only need a TEDI API key to access all aggregated data.

---

## Technical Implementation

### Frontend Component Structure

```vue
ApiKeysView.vue
├── Current API Key Display (computed maskedApiKey)
├── Create API Key Modal
│   ├── Form with validation
│   └── Success/Error handling
└── Usage Documentation Section
```

### State Management

```javascript
const showCreateModal = ref(false)      // Controls modal visibility
const loading = ref(false)              // Loading state during API calls
const error = ref(null)                 // Error messages
const createdKey = ref(null)            // Newly created key (shown once)
const newKey = ref({...})               // Form data for new key
```

### API Integration

The component uses `/src/services/api.js` to communicate with the backend:

```javascript
// Create new API key
const response = await api.auth.createKey({
  name: 'Production Key',
  owner_name: 'John Doe',
  owner_email: 'john@example.com',
  owner_organization: 'ACME Corp',
  scopes: ['agriculture:read'],
  expires_in_days: 365
})
```

### Backend Endpoint

**POST** `/api/v1/auth/keys`

**Request Body**:
```json
{
  "name": "Production Key",
  "owner_name": "John Doe",
  "owner_email": "john@example.com",
  "owner_organization": "ACME Corp",
  "scopes": ["agriculture:read"],
  "expires_in_days": 365
}
```

**Response** (201 Created):
```json
{
  "key": "tedi_prod_a1b2c3d4e5f6...xyz789",
  "id": 42,
  "name": "Production Key",
  "created_at": "2026-01-13T10:30:00Z",
  "expires_at": "2027-01-13T10:30:00Z"
}
```

**Note**: The `key` field is only returned once. Subsequent requests to view the key will return a masked version.

---

## Data Flow with Scheduler

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion Flow                      │
└─────────────────────────────────────────────────────────────┘

1. Scheduler runs (every 6 hours)
   ↓
2. Checks DatasetVersions due for update
   ↓
3. Dispatches tasks (FAOSTAT, World Bank, ILOSTAT, OSM)
   ↓
4. Connectors fetch data using external API credentials
   ↓
5. Data transformed and loaded into PostgreSQL
   ↓
6. IngestionLog created with stats
   ↓
7. DatasetVersion.last_checked_at updated
   ↓
8. ✓ Data now available via TEDI API

┌─────────────────────────────────────────────────────────────┐
│                      API Access Flow                        │
└─────────────────────────────────────────────────────────────┘

1. Client makes request with X-API-KEY header
   ↓
2. Backend validates API key in ApiKey table
   ↓
3. Checks scopes and rate limits
   ↓
4. Queries data from tables populated by scheduler
   ↓
5. Returns JSON response with metadata
   ↓
6. ✓ Client receives fresh, versioned data
```

---

## Usage Scenarios

### Scenario 1: Developer Creating First API Key

**Steps**:
1. Navigate to `/api-keys`
2. Click "Create New Key"
3. Fill in required information:
   - Name: "Development Testing"
   - Owner Name: "Alice Developer"
   - Email: "alice@company.com"
4. Submit form
5. **Important**: Copy the displayed API key immediately
6. Store it securely (e.g., environment variable, secrets manager)
7. Test the key:
   ```bash
   curl -H "X-API-KEY: tedi_dev_abc123...xyz789" \
     http://localhost:5000/api/v1/agriculture/communes
   ```

### Scenario 2: Organization with Multiple Keys

An organization might create separate keys for:
- **Production Key**: For live applications, long expiry (365 days)
- **Development Key**: For testing, shorter expiry (90 days)
- **Analytics Key**: For data analysis pipelines, restricted scopes

Each key can be managed independently and revoked if compromised.

### Scenario 3: Monitoring Data Updates

Developers can poll the API to detect new data:

```javascript
// Check if new data is available
async function checkForUpdates() {
  const response = await fetch('http://localhost:5000/api/v1/data-sources', {
    headers: { 'X-API-KEY': process.env.TEDI_API_KEY }
  })

  const sources = await response.json()

  sources.forEach(source => {
    console.log(`${source.name}: Last updated ${source.last_updated}`)
    console.log(`  Reliability: ${source.reliability_score}`)
    console.log(`  Next check: ${source.next_check_at}`)
  })
}
```

---

## Security Considerations

### Best Practices

1. **Never commit API keys to version control**
   - Use environment variables: `TEDI_API_KEY=tedi_prod_...`
   - Add `.env` to `.gitignore`

2. **Rotate keys periodically**
   - Create a new key before the old one expires
   - Update all applications
   - Revoke the old key

3. **Use appropriate expiry periods**
   - Production: 365 days (long-lived)
   - Development: 90 days (shorter rotation)
   - Testing: 30 days (frequent rotation)

4. **Monitor API usage**
   - Check rate limit headers in responses
   - Set up alerts for unusual activity
   - Review API logs regularly

5. **Principle of Least Privilege**
   - Request only necessary scopes
   - Future enhancement: More granular permissions (read-only vs. write)

### Key Storage

**Recommended**:
- Environment variables
- Secrets management systems (AWS Secrets Manager, HashiCorp Vault)
- Encrypted configuration files

**NOT Recommended**:
- Hardcoded in source code
- Stored in plain text files
- Shared via email or chat

---

## Future Enhancements

Planned improvements to the API Keys page:

1. **Key Management Dashboard**
   - List all created keys
   - View usage statistics per key
   - Revoke keys
   - Edit key metadata (name, organization)

2. **Advanced Scopes**
   - Granular permissions: `agriculture:read`, `employment:write`, `realestate:admin`
   - Scope-based access control in API responses

3. **Usage Analytics**
   - Requests per day/hour graph
   - Endpoint usage breakdown
   - Geographic distribution of requests

4. **Webhook Integration**
   - Subscribe to data update notifications
   - Receive alerts when new data is ingested
   - Event-driven architecture

5. **IP Whitelisting**
   - Restrict API key usage to specific IP addresses
   - Additional security layer for production keys

6. **API Key Rotation Helper**
   - Automated expiry reminders
   - One-click rotation with grace period
   - Deprecation warnings

---

## Troubleshooting

### Common Issues

#### 1. "Invalid API Key" Error

**Symptoms**: 401 Unauthorized response

**Causes**:
- Expired key
- Typo in key value
- Missing `X-API-KEY` header

**Solution**:
```bash
# Verify header format
curl -v -H "X-API-KEY: your-key-here" http://localhost:5000/api/v1/agriculture/communes

# Check for spaces or newlines in key
echo -n "your-key-here" | wc -c  # Should match expected length
```

#### 2. Rate Limit Exceeded

**Symptoms**: 429 Too Many Requests

**Causes**:
- Exceeded 1,000 requests/hour
- Exceeded 10,000 requests/day

**Solution**:
- Implement exponential backoff in client code
- Check `X-RateLimit-Remaining` header
- Cache responses to reduce API calls
- Request higher limits for production use cases

#### 3. API Key Not Showing After Creation

**Issue**: Closed modal before copying the key

**Resolution**: API keys are only shown once for security. If lost:
1. Create a new API key
2. Update applications with new key
3. Optionally contact support to revoke lost key

---

## Related Documentation

- [DASHBOARD.md](./DASHBOARD.md) - Dashboard page with ingestion statistics
- [MAP_PAGE.md](./MAP_PAGE.md) - Interactive map showing commune data
- [Backend API Documentation](http://localhost:5000/api/docs) - Full API reference
- [Backend Scheduler Guide](../../backend/QUICKSTART_TESTING.md) - Testing the data ingestion system

---

## Contact & Support

For issues with API keys or access:
- Technical documentation: http://localhost:5000/api/docs
- Backend logs: Check `docker logs tedi_backend`
- Ingestion status: Query `/api/v1/ingestion-logs` endpoint

---

**Last Updated**: 2026-01-13
**Component**: `/frontend/src/views/ApiKeysView.vue`
**Backend**: `/backend/app/routes/auth.py` (API key management routes)
