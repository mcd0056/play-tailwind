FROM python:3.9

WORKDIR /usr/src/app

COPY . .

# Install dependencies required for psycopg2 binary
RUN apt-get update && apt-get install -y libpq-dev gcc

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
