# ==========================================
# STAGE 1: Build the React Frontend (Vite)
# ==========================================
FROM node:18-alpine AS build-stage

WORKDIR /app/frontend

# Copy package files and install frontend dependencies
COPY truthlens-frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend code and build it
COPY truthlens-frontend/ ./
RUN npm run build


# ==========================================
# STAGE 2: Setup FastAPI Backend
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY truthlens-backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY truthlens-backend/ ./

# Copy the built Vite files from STAGE 1 into a 'static' folder in the backend
COPY --from=build-stage /app/frontend/dist ./static

# Expose the port Koyeb and FastAPI will use
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]