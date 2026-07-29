FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 确认复制到 /app/ 目录
COPY main.py .
COPY config.yaml .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# 修改 CMD：明确指定工作目录和模块路径
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]