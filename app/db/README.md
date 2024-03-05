---
runme:
  id: 01HR5294NFFNAT2JMDQFNS2D7Y
  version: v3
---

# Chat Management and Feedback API Service

This FastAPI-powered service manages chat conversations and feedback, supporting the creation of new conversations from a chatbot server, and updating and adding feedback to conversations. It provides robust filtering for admin oversight, utilizes MongoDB for data storage, and is designed for high performance and scalability.

## Key Features

- **Conversation Management**: Create and store new conversations initiated by the chatbot server.
- **Feedback Handling**: Add and update feedback for conversations.
- **Admin Filtering**: Advanced filtering options on the admin page.
- **Secure Access**: JWT for secure API access.
- **Automated Documentation**: FastAPI's automatic OpenAPI doc generation.

## Getting Started

### Prerequisites

- Docker
- Docker Compose (for development)

### Installation with Docker

Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chat-management-feedback-server.git
   cd chat-management-feedback-server
```

## Use the Makefile to build and run the Docker container:

```bash
make build
make up
```

Alternatively, if you prefer not to use the Makefile:

```bash
docker build -t chat-management-feedback-api .
docker run -d --name chat-api -p 8000:8000 chat-management-feedback-api
```

## Accessing the API
Once the Docker container is running, the API is accessible at `http://localhost:8000`. Visit `http://localhost:8000/docs` or `http://localhost:8000/redoc` for interactive API documentation.

## Development
To facilitate development, a `docker-compose.yml` file is provided. Use the following command to start the development server with live reload:

```bash
make dev
```

Or directly with Docker Compose:

```bash
docker-compose up
```

## CI/CD with GitHub Actions
This project is configured with GitHub Actions for Continuous Integration and Continuous Deployment. On every push to the main branch, GitHub Actions will:

- Run tests.
- Build the Docker image.
- Push the Docker image to the registry (configure registry details in the GitHub Actions workflow file).

## Running Tests
To run tests within the Docker environment, use:

```bash
make test
```

Or execute directly:

```bash
docker exec -it chat-api pytest
```

## Deployment
Deployment instructions are specific to your target environment (AWS, GCP, Azure, etc.). Ensure your deployment environment has Docker installed and configure your CI/CD pipeline to deploy the Docker container after successful build and test runs.

## Built With:
- **FastAPI** - The web framework used
- **MongoDB** - Database
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Gunicorn** - WSGI HTTP Server
- **python-dotenv** - Environment variable management
- **PyJWT** - JSON Web Tokens for authentication
- **Docker** - Containerization
- **Makefile** - Simplified command execution
- **GitHub Actions** - CI/CD