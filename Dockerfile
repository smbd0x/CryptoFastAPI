FROM python:3.13-slim

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install pytest pytest-asyncio

COPY . .

CMD ["pytest", "-sv"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]