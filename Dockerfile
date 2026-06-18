# ----- Build Stage -----
FROM python:3.11-slim AS builder

WORKDIR /app

# Create a virtual environment and install dependencies into it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----- Run Stage -----
FROM python:3.11-slim

WORKDIR /app

# Copy only the compiled virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the actual application code
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
