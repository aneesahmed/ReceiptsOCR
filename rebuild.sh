docker rm -f my-ocr-service && \
docker build -t receipt-ocr-app . && \
docker run -d -p 8000:8000 --name my-ocr-service receipt-ocr-app