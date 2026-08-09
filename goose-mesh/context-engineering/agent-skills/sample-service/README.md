# Sample Service

A dependency-free Python HTTP service used to demonstrate the `release-readiness` Goose Agent Skill.

## Run

```bash
python3 src/service.py
curl http://127.0.0.1:8080/health
```

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Container

```bash
docker build -t sample-service .
docker run --rm -p 8080:8080 sample-service
```
