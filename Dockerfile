# Sử dụng image Python chính thức từ Docker Hub
FROM python:3.11-slim-bookworm
# Thiết lập biến môi trường (tùy chọn)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements.txt vào container và cài đặt các dependencies
COPY requirements.txt .

# Cài đặt các thư viện phụ thuộc được liệt kê trong requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

EXPOSE 8000

# Chạy ứng dụng (giả sử app.py là file chính)
CMD uvicorn main:app --host 0.0.0.0 --port 8000
