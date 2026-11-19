# Expense Flow API

Expense Flow API

A FastAPI-based Expense Management System that provides APIs for managing expenses, categories, and users.

Features

Create, update, and delete expenses

Categorize expenses

User management

SQLite database integration

Repository pattern implementation

Pydantic schema validation

RESTful API design

Expense Flow API

A FastAPI-based Expense Management System that provides APIs for managing expenses, categories, and users.

Features

Create, update, and delete expenses

Categorize expenses

User management

SQLite database integration

Repository pattern implementation

Pydantic schema validation

RESTful API design

Project Structure

expense\_flow\_api/

│

├── app/

│   ├── api/

│   ├── core/

│   ├── db/

│   ├── models/

│   ├── repositories/

│   └── services/

│

├── expenseflow.db

├── pyproject.toml

├── reset\_db.py

├── show\_db.py

└── README.md

Technology Stack

Python 3.11+

FastAPI

SQLAlchemy

Pydantic

SQLite

Uvicorn

Installation

Clone Repository

git clone https://github.com/banothulaxmiprasanna/expense-flow-api.git

cd expense-flow-api

Create Virtual Environment

python -m venv venv

Activate:

Windows

venv\\Scripts\\activate

Linux/Mac

source venv/bin/activate

Install Dependencies

pip install -e .

Run Application

uvicorn app.main:app --reload

Application URL:

http://127.0.0.1:8000

API Documentation

Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

Database

The application uses SQLite.

Database file:

expenseflow.db

Reset Database

python reset\_db.py

View Database

python show\_db.py

Example Expense Payload

{

&#x20; "title": "Lunch",

&#x20; "amount": 250,

&#x20; "category\_id": 1,

&#x20; "description": "Team lunch"

}

Future Enhancements

JWT Authentication

Expense Reports

Budget Tracking

User Roles and Permissions

Docker Support

PostgreSQL Integration

1\. Architecture/Design Section

Architecture

The application follows a layered architecture:



API Layer - Handles HTTP requests and responses

Service Layer - Contains business logic

Repository Layer - Handles database operations

Model Layer - Defines database tables

Database Layer - SQLite with SQLAlchemy ORM

This design improves maintainability, scalability, and testability 

2\. Sample API Endpoints

Sample Endpoints

Method	Endpoint	Description

GET	/expenses	Get all expenses

GET	/expenses/{id}	Get expense by ID

POST	/expenses	Create expense

PUT	/expenses/{id}	Update expense

DELETE	/expenses/{id}	Delete expense

3\. Author Information

Author

Banothu Laxmiprasanna



GitHub: https://github.com/banothulaxmiprasanna







&#x20;

