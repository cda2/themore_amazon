FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY themore_amazon /app/themore_amazon
COPY poetry.lock pyproject.toml /app/

# Update apt-get
RUN apt-get update

# Install any needed packages specified in pyproject.toml
RUN python -m pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Playwright dependencies
RUN python -m playwright install firefox
RUN python -m playwright install-deps

# Xvfb run install
RUN apt-get install -y xvfb xauth

# Run the application
CMD ["xvfb-run", "python", "-m", "themore_amazon"]
