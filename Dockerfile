FROM python:3.11-alpine AS builder

RUN apk add poetry

COPY . /build
WORKDIR /build

RUN poetry build --format wheel

FROM python:3.11-alpine

COPY --from=builder /build/dist/*.whl /root
RUN pip install /root/*.whl

CMD python -m picobot
