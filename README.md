# ATS (Applicant Tracking System)

A Django REST Framework based ATS system for recruiters to track job applications. The system provides APIs for managing candidates and includes a sophisticated search functionality that sorts results based on name relevancy.

## Features

- CRUD operations for candidate management
- Advanced search functionality with relevancy-based sorting
- Input validation and error handling
- RESTful API design

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Candidates

#### Create Candidate
```bash
POST /api/candidates/
Content-Type: application/json

{
    "name": "John Doe",
    "age": 25,
    "gender": "M",
    "email": "john@example.com",
    "phone_number": "1234567890"
}
```

#### Update Candidate
```bash
PUT /api/candidates/{id}/
Content-Type: application/json

{
    "name": "John Doe",
    "age": 26,
    "gender": "M",
    "email": "john@example.com",
    "phone_number": "1234567890"
}
```

#### Delete Candidate
```bash
DELETE /api/candidates/{id}/
```

#### Search Candidates
```bash
GET /api/candidates/search/?query=Ajay Kumar yadav
```

The search results are sorted by relevancy using the following criteria:
1. Exact matches first
2. Number of matching words (descending)
3. Last name matches
4. First name matches
5. Word order score
6. Alphabetical order

Example search results for "Ajay Kumar yadav":
1. "Ajay Kumar Yadav" (exact match)
2. "Ajay Kumar" (2 matches)
3. "Ajay Yadav" (2 matches)
4. "Kumar Yadav" (2 matches)
5. "Ramesh Yadav" (1 match + last name)
6. "Ajay Singh" (1 match)

#### Get Candidate Statistics
```bash
GET /api/candidates/statistics/
```

Returns:
```json
{
    "total_candidates": 6,
    "gender_distribution": [
        {"gender": "M", "count": 6}
    ],
    "age_statistics": {
        "avg_age": 30.0,
        "min_age": 20,
        "max_age": 45
    }
}
```

## Data Validation

### Candidate Model
- Name: Letters and spaces only
- Age: 18-100 years
- Gender: M (Male), F (Female), O (Other)
- Email: Unique, valid email format
- Phone Number: Exactly 10 digits

### Error Responses
All API endpoints return appropriate HTTP status codes and error messages in the following format:
```json
{
    "status": "error",
    "message": "Error message here"
}
```

## Testing

Run the test suite:
```bash
python manage.py test candidates
```

Test cases cover:
- CRUD operations
- Search functionality
- Input validation
- Error handling

## Project Structure
ats_project/
├── candidates/
│ ├── models.py # Candidate model definition
│ ├── serializers.py # Data serialization
│ ├── views.py # API views and logic
│ ├── urls.py # URL routing
│ └── tests/ # Test cases
├── ats_project/
│ ├── settings.py # Project settings
│ └── urls.py # Main URL configuration
└── manage.py