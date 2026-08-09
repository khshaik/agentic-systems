FROM python:3.13-slim

WORKDIR /app
COPY src/service.py /app/service.py
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8080
CMD ["python", "/app/service.py"]
