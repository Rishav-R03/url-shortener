URL Shortener with Analytics and Caching
Table of Contents
Introduction

Features

Technologies Used

Project Structure

Database Schema

Getting Started

Prerequisites

Running with Docker Compose (Recommended)

Running Locally (Without Docker)

Testing

API Endpoints

Future Enhancements

Challenges & Learnings

Contributing

License

1. Introduction
This project implements a robust and efficient URL shortening service, designed to convert long, unwieldy URLs into short, shareable codes. Beyond basic shortening and redirection, it incorporates essential features like click analytics, high-speed caching with Redis, and basic rate limiting to ensure reliability and prevent abuse. The entire application is built using modern asynchronous Python frameworks and is fully containerized with Docker for easy deployment and scalability.

2. Features
URL Shortening: Convert any long URL into a unique, concise short code.

Fast Redirection: Redirect users from a short URL to its original long URL with minimal latency.

Basic Click Analytics: Track the total number of times each short URL has been accessed.

Redis Caching: Store frequently accessed URL mappings in Redis to significantly speed up redirection by reducing direct database hits.

Rate Limiting: Protect the URL creation endpoint from excessive requests and potential abuse.

Containerized Deployment: Utilize Docker and Docker Compose for a consistent and isolated development and production environment.

Automated Testing: Comprehensive test suite using Pytest to ensure reliability and correctness of the API.

3. Technologies Used
Backend:

FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.8+ based on standard Python type hints.

SQLAlchemy: The Python SQL Toolkit and Object Relational Mapper (ORM) for efficient database interactions.

AsyncPG: A fast PostgreSQL database client library for Python/asyncio.

Redis: An open-source, in-memory data structure store, used as a database, cache, and message broker.

Pydantic: Data validation and settings management using Python type hints.

Shortuuid: A library for generating concise, unambiguous, and URL-safe UUIDs.

Database:

PostgreSQL: A powerful, open-source object-relational database system.

Containerization:

Docker: Platform for developing, shipping, and running applications in containers.

Docker Compose: Tool for defining and running multi-container Docker applications.

Testing:

Pytest: A mature full-featured Python testing framework.

Pytest-Asyncio: Pytest plugin for testing asyncio code.

HTTPX: A fully featured HTTP client for Python, used for making asynchronous requests in tests.

4. Project Structure
<img width="898" height="462" alt="Screenshot 2025-07-20 121026" src="https://github.com/user-attachments/assets/c30b2e29-6dd5-4d9e-a7b2-e7ff7559866b" />


5. Database Schema
<img width="957" height="597" alt="Screenshot 2025-07-20 120938" src="https://github.com/user-attachments/assets/de68c5a1-3025-47c2-b276-8d98d9079d5b" />
<img width="344" height="647" alt="Screenshot 2025-07-20 121213" src="https://github.com/user-attachments/assets/2bdfb728-ac33-4df1-ac9a-856a47deea1a" />


6. Getting Started
Prerequisites
Before you begin, ensure you have the following installed:

Git

Docker Desktop (includes Docker Engine and Docker Compose) - Recommended for seamless setup.

Python 3.11+ (if running locally without Docker)

PostgreSQL (if running locally without Docker)

Redis (if running locally without Docker)

Running with Docker Compose (Recommended)
This is the easiest way to get the entire application stack (FastAPI, PostgreSQL, Redis) up and running.

Clone the repository:

git clone [Github](https://github.com/Rishav-R03/url-shortener/)
cd url_shortener

Build and start the services:

docker-compose up --build -d

--build: Builds the app Docker image.

-d: Runs the containers in detached mode (in the background).

Verify services are running:

docker-compose ps

You should see db, redis, and app containers in an Up (healthy) state.

Access the API documentation:
Open your web browser and navigate to:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Running Locally (Without Docker)
If you prefer to run the FastAPI application directly on your host machine, you need to have PostgreSQL and Redis installed and running locally or in a VM.

Install PostgreSQL and Redis locally:

PostgreSQL: Install from PostgreSQL Downloads. Create a database named url_shortener_db and a user user with password password.

CREATE DATABASE url_shortener_db;
CREATE USER "user" WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE url_shortener_db TO "user";

Redis:

Linux/macOS: Install via package manager (e.g., sudo apt install redis-server on Ubuntu, brew install redis on macOS). Start the service.

Windows: The most reliable way is via WSL (Windows Subsystem for Linux). Install Ubuntu in WSL, then install and start redis-server within the Ubuntu terminal.

Create and activate a Python virtual environment:

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

Install Python dependencies:

pip install -r requirements.txt

Update app/config.py for local connections:
Ensure REDIS_HOST is set to localhost (if Redis is running directly on your machine or via WSL port forwarding) or the specific IP of your VM if Redis is in a VM. DATABASE_URL should also point to localhost.

# app/config.py excerpt
DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/url_shortener_db"
REDIS_HOST: str = "localhost" # Or your VM's IP like "172.xx.xx"
REDIS_PORT: int = 6379

Run the FastAPI application:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Access Swagger UI: http://localhost:8000/docs

7. Testing
The project includes a comprehensive test suite using pytest to ensure the reliability of the API endpoints.

Ensure test database is running:
If using Docker Compose, the db_test service will be started automatically.
If running tests locally, ensure you have a separate PostgreSQL instance for testing (e.g., on port 5433) with a database named test_url_shortener_db and the same user/password credentials.

Install test dependencies:
Ensure pytest, pytest-asyncio, and httpx are installed (included in requirements.txt).

Run tests from the project root directory:

pytest

8. API Endpoints
POST /shorten

Description: Creates a new short URL for a given long URL.

Request Body:

{
  "long_url": "https://www.example.com/very/long/url"
}

Response (201 Created):

{
  "short_code": "abc123de",
  "long_url": "https://www.example.com/very/long/url",
  "created_at": "2023-10-27T10:00:00.000Z",
  "id": 1
}

GET /{short_code}

Description: Redirects to the original long URL and records a click event.

Path Parameter: short_code (e.g., abc123de)

Response (307 Temporary Redirect): Redirects the client to the long_url.

GET /analytics/{short_code}

Description: Retrieves analytics for a specific short URL, including total clicks.

Path Parameter: short_code (e.g., abc123de)

Response (200 OK):

{
  "short_code": "abc123de",
  "long_url": "https://www.example.com/very/long/url",
  "created_at": "2023-10-27T10:00:00.000Z",
  "total_clicks": 5
}

9. Future Enhancements
This project provides a robust foundation. Here are some ideas for future development:

User Authentication & Management: Implement user accounts to allow users to manage their own short URLs.

Custom Short Codes: Allow users to define their preferred short codes if available.

Advanced Analytics: Track referrer, user agent (browser/OS/device), and geographical location of clicks.

URL Expiration: Enable setting an expiration date/time for short URLs.

QR Code Generation: Provide an endpoint to generate QR codes for short URLs.

Custom Domains: Support using custom domains for shortened links (e.g., yourbrand.com/abc).

Asynchronous Click Aggregation: Use a background task (e.g., Celery) to periodically move click counts from Redis to PostgreSQL for long-term storage, reducing immediate DB writes.

Improved Rate Limiting: Implement more sophisticated, distributed rate limiting using Redis.

Container Health Checks: Add health checks for the app service in docker-compose.yml.

10. Challenges & Learnings
Throughout this project, several common but significant challenges were encountered, providing valuable insights into building robust applications:

Docker Volume Management: Understanding how Docker volumes persist data and how to clear them (docker-compose down -v) was crucial for resolving database authentication and configuration issues.

Asynchronous Database Connectivity: Debugging asyncpg and SQLAlchemy errors related to connection states and event loop management required careful handling of asynchronous contexts and retries.

Inter-Container Networking: Resolving getaddrinfo failed and ConnectionRefusedError highlighted the importance of correct service naming in docker-compose.yml and proper network configuration for local development (e.g., Host-Only Adapter IPs, Port Forwarding, VM firewalls).

Pytest Fixture Scoping: Learning to correctly scope pytest-asyncio fixtures (session vs. function) was essential for ensuring isolated and reliable tests.

Debugging Strategies: The iterative process of checking Docker logs (docker-compose logs --follow), verifying container status (docker-compose ps), and manually inspecting database/Redis states proved invaluable for pinpointing root causes.

11. Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

12. License
This project is open-source and available under the MIT License.
