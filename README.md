# Tornado Test Application

This repository contains a simple web application built using the Tornado web framework and PostgreSQL as the database. The application provides basic CRUD operations for managing users and includes a frontend form for user creation.

## Features

- **Frontend**: A simple HTML form to insert user details.
- **Backend**: Tornado-based server with endpoints for:
    - Creating users
    - Fetching all users
    - Updating user details
- **Database**: PostgreSQL integration for persistent data storage.
- **Validation**: Input validation for required fields.
- **Dockerized Setup**: Easy setup using Docker Compose.

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.
- Python 3.8+ (if running locally without Docker).
- PostgreSQL installed (if running locally without Docker).

## Setup Instructions

### Using Docker Compose

1. Clone the repository:
     ```bash
     git clone <repository-url>
     cd tornado_test
     ```

2. Start the application using Docker Compose:
     ```bash
     docker-compose up
     ```

3. Access the application:
     - Frontend: [http://localhost:8888](http://localhost:8888)
     - Backend API:
         - `GET /users`: Fetch all users.
         - `POST /users`: Create a new user.
         - `PUT /users`: Update an existing user.

4. Stop the application:
     ```bash
     docker-compose down
     ```

### Running Locally

1. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. Set up the PostgreSQL database:
     - Create a database named `test`.
     - Update the connection details in `server.py` if necessary.

3. Run the server:
     ```bash
     python server.py
     ```

4. Access the application:
     - Frontend: [http://localhost:8888](http://localhost:8888)
     - Backend API:
         - `GET /users`: Fetch all users.
         - `POST /users`: Create a new user.
         - `PUT /users`: Update an existing user.

## File Structure

```
tornado_test/
├── docker-compose.yaml   # Docker Compose configuration
├── requirements.txt      # Python dependencies
├── server.py             # Tornado server implementation
├── templates/            # HTML templates
│   └── index.html        # Frontend form for user creation
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## API Endpoints

### `GET /users`
- Fetches all users from the database.
- **Response**:
    ```json
    {
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"}
        ]
    }
    ```

### `POST /users`
- Creates a new user.
- **Request Body**:
    ```json
    {
        "name": "John Doe",
        "email": "john@example.com"
    }
    ```
- **Response**:
    ```json
    {
        "id": 1,
        "message": "User created"
    }
    ```

### `PUT /users`
- Updates an existing user.
- **Request Body**:
    ```json
    {
        "id": 1,
        "name": "Jane Doe",
        "email": "jane@example.com"
    }
    ```
- **Response**:
    ```json
    {
        "message": "User updated"
    }
    ```

## Security Note

The repository contains a sample private key (`secret.pem`) for demonstration purposes. **Do not use this key in production environments.** Always generate and manage your private keys securely.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Tornado Web Framework](https://www.tornadoweb.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)  