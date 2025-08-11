## Payment Terminal Backend

This repository contains the backend services for a crypto payment terminal. It is a production-grade system designed to handle payments from both web-based virtual terminals and physical ISO 8583 card terminals.

### Architecture
The project is built with a modular, multi-service architecture:

-   **`app.py`**: The central Flask application that defines the public-facing API for processing and deleting transactions.
-   **`iso_gateway.py`**: A dedicated service for handling raw TCP/IP connections from physical terminals.
-   **`payment_processor.py`**: A core module that contains the business logic for transaction validation and crypto payouts.

### Getting Started

#### Prerequisites
-   Python 3.8 or higher
-   Git

#### Installation
1.  **Clone the Repository**:
    ```sh
    git clone [https://github.com/your-username/payment-terminal-backend.git](https://github.com/your-username/payment-terminal-backend.git)
    cd payment-terminal-backend
    ```

2.  **Create a Virtual Environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

#### Configuration
You will need to set the following environment variables for your deployment (e.g., on Render):

-   `FLASK_SECRET_KEY`: A long, random string for session security.
-   `BACKEND_PROCESSOR_URL`: The URL of your deployed `app.py` service.
-   `__firebase_config`: Your Firebase Admin SDK JSON credentials.
-   `__app_id`: Your unique application ID.

### Deployment

To deploy this project to a service like Render, you would typically:

1.  **Push the code to a Git provider** (like GitHub).
2.  **Connect Render** to your repository.
3.  **Create a new Web Service** and configure the environment variables as listed above. Render will automatically use the `Procfile` to run the application.
