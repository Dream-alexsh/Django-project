FROM python:3.10-slim

WORKDIR opt/todolist

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY todolist/ ./
COPY entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "runbot"]
EXPOSE 8000