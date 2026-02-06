# 1. Use an official lightweight Python image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements and install them
# (We install directly here to keep it simple for the MVP)
RUN pip install --no-cache-dir fastapi uvicorn requests

# 4. Copy your Application Code into the container
COPY . .

# 5. Initialize the Database inside the container
RUN python database.py

# 6. Open the "Door" (Port 8000)
EXPOSE 8000

# 7. Start the Engine when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]