FROM python:3.12-slim
WORKDIR /app

# RUN apt update
# RUN apt install -y python3
# RUN apt clean
# RUN rm -rf /var/lib/apt/lists/*

RUN pip install poetry
RUN poetry config virtualenvs.create

COPY ./pyproject.toml ./poetry.lock* ./
RUN poetry install

COPY ./blog_backend ./blog_backend

VOLUME ["/app/data", "/app/static"]
EXPOSE 3000

CMD ["poetry", "run", "task", "prod"]
