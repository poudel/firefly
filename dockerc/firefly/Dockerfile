FROM python:3.7.0-slim-stretch

RUN groupadd -r firefly  \
  && useradd -r -g firefly firefly

RUN apt-get update && apt-get -y install build-essential

COPY ./dockerc/firefly/start.sh /
COPY ./dockerc/firefly/entrypoint.sh /

WORKDIR /app
COPY . /app

RUN pip install pipenv
RUN sed -i 's/\r//' /start.sh \
  && sed -i 's/\r//' /entrypoint.sh \
  && chmod +x /entrypoint.sh \
  && chown firefly /entrypoint.sh \
  && chmod +x /start.sh \
  && chown firefly /start.sh

# RUN pipenv install --skip-lock
RUN pipenv install --dev --skip-lock

ENTRYPOINT ["/entrypoint.sh"]
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
