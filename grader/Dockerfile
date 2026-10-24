# 只用来跑评测和灌本地数据，不参与 MySQL 服务。
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 装上 mysql 客户端，方便在容器里 source db/*.sql
RUN apt-get update \
 && apt-get install -y --no-install-recommends default-mysql-client \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /work
CMD ["python", "grader/run.py", "--part", "all"]
