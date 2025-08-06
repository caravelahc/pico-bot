FROM python:3.11-alpine AS builder

RUN apk add uv

COPY . /build
WORKDIR /build

RUN uv sync

FROM python:3.11-alpine

COPY --from=builder /build/dist/*.whl /root
RUN pip install /root/*.whl

CMD python -m picobot
