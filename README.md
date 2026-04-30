# ReachBridge

A FastAPI-based backend system for ingesting, processing, and serving HR and company contact data from Excel files.

## Overview

ReachBridge provides a robust API pipeline for:
- Multi-sheet Excel file ingestion and parsing
- Data normalization and validation
- Contact deduplication and cleaning
- Structured REST API access to processed data

## Features

- **Dynamic Excel Parsing**: Handles multi-sheet Excel files with flexible column mapping
- **Data Normalization**: Standardizes inconsistent column names (Company vs Company Name, Mobile vs Phone)
- **Validation**: Email validation and phone number cleaning
- **Deduplication**: Removes duplicates based on email, mobile, and landline numbers
- **Clean API Responses**: Automatically removes null/invalid fields from responses
- **Rate Limiting**: Basic IP-based rate limiting for API protection
- **Modular Architecture**: Clean separation of concerns with routers, services, and models

## Tech Stack

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Development database (PostgreSQL support included)
- **Pandas + OpenPyXL**: Excel file processing
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization

## Project Structure

```
job_platform/
├── app/
│   ├── routers/           # API route definitions
│   │   ├── contacts.py    # Contact retrieval endpoints
│   │   ├── upload.py      # Excel upload endpoints
│   │   ├── stats.py       # Statistics endpoints
│   │   └── submit.py      # Data submission endpoints
│   ├── models/            # Database models
│   │   └── models.py      # SQLAlchemy model definitions
│   ├── services/          # Business logic services
│   │   ├── excel_parser.py    # Excel file parsing logic
│   │   ├── limiter.py         # Rate limiting implementation
│   │   └── utils.py           # Utility functions
│   ├── schemas/           # Pydantic schemas
│   ├── database.py        # Database configuration
│   └── main.py           # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job_platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

### Option 1: Direct Python
1. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - OpenAPI Schema: http://localhost:8000/openapi.json

### Option 2: Docker (Development)
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Option 3: Docker (Production)
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## Deployment

### Production Deployment with Docker

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

2. **Deploy**
   ```bash
   ./deploy.sh
   ```

3. **Services**
   - **API**: http://localhost:8000
   - **Database**: PostgreSQL on port 5432
   - **Nginx**: HTTP proxy on port 80

### Docker Compose Services

- **app**: FastAPI application
- **db**: PostgreSQL database
- **nginx**: Reverse proxy with rate limiting

### Environment Variables

Key environment variables for production:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/database
ENVIRONMENT=production
SECRET_KEY=your-secret-key
MAX_FILE_SIZE=50MB
```

## API Endpoints

### Upload Excel File
```http
POST /upload-excel
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST "http://localhost:8000/upload-excel" \
     -F "file=@contacts.xlsx"
```

**Response:**
```json
{
  "message": "Excel file processed successfully",
  "total_contacts": 150,
  "sheets_processed": ["HR_Contacts", "Company_Leads"]
}
```

### Get All Contacts
```http
GET /contacts
```

**Response:**
```json
{
  "contacts": [
    {
      "id": 1,
      "name": "John Doe",
      "company": "Acme Corp",
      "email": "john@acme.com",
      "mobile": "+1234567890",
      "landline": "+1987654321",
      "sheet": "HR_Contacts"
    }
  ],
  "total": 1
}
```

### Get Contacts by Sheet
```http
GET /contacts?sheet=HR_Contacts
```

**Response:**
```json
{
  "contacts": [
    {
      "id": 1,
      "name": "John Doe",
      "company": "Acme Corp",
      "email": "john@acme.com",
      "mobile": "+1234567890",
      "sheet": "HR_Contacts"
    }
  ],
  "total": 1,
  "sheet": "HR_Contacts"
}
```

### Get Contact by ID
```http
GET /contacts/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "company": "Acme Corp",
  "email": "john@acme.com",
  "mobile": "+1234567890",
  "landline": "+1987654321",
  "sheet": "HR_Contacts"
}
```

### Get Available Sheets
```http
GET /contacts/sheets
```

**Response:**
```json
{
  "sheets": ["HR_Contacts", "Company_Leads", "Partners"]
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ReachBridge API",
  "version": "1.0.0"
}
```

## Data Processing

### Column Normalization
The system automatically normalizes common column variations:
- `Company`, `Company Name`, `Organization` → `company`
- `Mobile`, `Phone`, `Cell` → `mobile`
- `Landline`, `Office`, `Work Phone` → `landline`

### Phone Number Cleaning
- Removes formatting characters
- Validates phone number patterns
- Separates mobile from landline numbers

### Email Validation
- Basic format validation
- Removes invalid email entries
- Handles case insensitivity

### Deduplication
Contacts are deduplicated based on:
- Email address (primary)
- Mobile number (secondary)
- Landline number (tertiary)

## Limitations

- **Database**: Uses SQLite for development (not production-ready)
- **Authentication**: No built-in authentication or authorization
- **Rate Limiting**: Basic IP-based limiting only
- **File Size**: Limited by server memory for Excel processing
- **Concurrent Uploads**: No queue system for large file processing

## Future Improvements

### Database & Performance
- [ ] PostgreSQL integration for production
- [ ] Database connection pooling
- [ ] Query optimization and indexing
- [ ] Data migration tools

### Security & Authentication
- [ ] JWT-based authentication
- [ ] Role-based access control
- [ ] API key management
- [ ] HTTPS enforcement

### Rate Limiting & Scaling
- [ ] Redis-based rate limiting
- [ ] Distributed processing
- [ ] File upload queuing system
- [ ] Background task processing

### Features
- [ ] Advanced search and filtering
- [ ] Pagination for large datasets
- [ ] Data export functionality
- [ ] Bulk operations
- [ ] Audit logging
- [ ] Data visualization endpoints

### Monitoring & Observability
- [ ] Structured logging
- [ ] Metrics collection
- [ ] Health check endpoints
- [ ] Performance monitoring

## Development Notes

### Adding New Sheets
When uploading Excel files with new sheet names, the system automatically:
- Creates new sheet entries in the database
- Processes data using existing normalization rules
- Makes contacts available via the API immediately

### Error Handling
The API provides detailed error messages for:
- Invalid file formats
- Corrupted Excel files
- Missing required columns
- Data validation failures

### Logging
Basic logging is implemented for:
- File upload operations
- API access patterns
- Rate limiting violations

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
