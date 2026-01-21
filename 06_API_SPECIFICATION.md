
# API SPECIFICATION

## Authentication
- API Key via header: X-API-KEY

## Agriculture
GET /api/v1/agriculture/communes
GET /api/v1/agriculture/crops
GET /api/v1/agriculture/index?commune_id=&year=

## Real Estate
GET /api/v1/real-estate/index

## Employment
GET /api/v1/employment/index

## Business
GET /api/v1/business/index

## Response Format
{
  "data": [],
  "metadata": {
    "source": "",
    "updated_at": ""
  }
}
