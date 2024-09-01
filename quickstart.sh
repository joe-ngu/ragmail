#!/bin/bash

# List of environment variables to be required
REQUIRED_ENV_VARS=("DATABASE_URL" "SECRET_KEY" "DEBUG")

# Function to create .env file
create_env_file() {
    echo ".env file not found."
    touch .env
    echo "Creating .env file. Please enter the values for the following environment variables:"

    for var in "${REQUIRED_ENV_VARS[@]}"; do
        read -p "Enter value for $var: " value
        echo "$var=$value" >> .env
    done

    echo ".env file created with the provided environment variables."
}

# Function to run the app
run_app() {
    echo "Running app.py..."
    python app.py
}

# Main script logic
if [ ! -f ".env" ]; then
    create_env_file
else
    echo ".env file already exists."
fi

run_app
