How to launch website:
How to Run CareConnect App Locally

This guide will walk you through setting up and running the CareConnect application (both backend and frontend) on your local machine.

Prerequisites

Before you begin, ensure you have the following installed:

•
Python 3.8+: For the Flask backend.

•
Node.js 18+: For the React frontend (includes npm/pnpm).

•
Git: For cloning the repository.

1. Clone the Repository

First, clone the CareConnect repository from GitHub:

Bash


git clone https://github.com/fish9274/CareConnectHK.git
cd CareConnectHK


2. Set up the Backend (Flask API)

Navigate to the elder_care_api directory and set up the Flask backend.

Bash


cd elder_care_api

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask application
# The app will run on http://127.0.0.1:5000 by default
python src/main.py


Leave this terminal window open and the Flask server running. You should see output indicating the server is running on http://127.0.0.1:5000.

3. Set up the Frontend (React App)

Open a new terminal window, navigate back to the CareConnectHK root directory, and then into the elder-care-platform directory.

Bash


# From the CareConnectHK root directory
cd elder-care-platform

# Install Node.js dependencies using pnpm (recommended) or npm
pnpm install
# or npm install

# Start the React development server
# The app will run on http://localhost:5173 by default
pnpm run dev
# or npm run dev


Leave this terminal window open and the React development server running. You should see output indicating the server is running on http://localhost:5173.

4. Access the Application

Once both the Flask backend and React frontend servers are running, open your web browser and navigate to:

http://localhost:5173

You should now see the CareConnect application running locally in your browser.

Troubleshooting

•
Port already in use: If you encounter an error like Address already in use for the Flask app, it means another process is using port 5000. You can either stop that process or try running the Flask app on a different port (e.g., flask run --port 5001).

•
Frontend not connecting to backend: Ensure both servers are running and that the frontend is trying to connect to the correct backend URL (which is http://localhost:5000 by default in the provided code).

•
Missing dependencies: Double-check that all dependencies were installed correctly for both the backend (pip install -r requirements.txt) and frontend (pnpm install or npm install).

If you have any further issues, please let me know!

