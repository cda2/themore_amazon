FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY themore_amazon /app/themore_amazon
COPY pyproject.toml /app/

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Install the required packages
RUN /root/.cargo/bin/uv pip compile pyproject.toml -o requirements.txt \
    && /root/.cargo/bin/uv pip install -r requirements.txt -n --no-deps --system \
    && rm requirements.txt

# Install Playwright dependencies, but only Firefox for image size
RUN playwright install firefox --with-deps

# Update apt-get && Xvfb run install
RUN apt-get update && apt-get install -y xvfb xauth

# Run the application
CMD ["xvfb-run", "python", "-m", "themore_amazon"]