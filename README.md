# TowerX 🚀

**TowerX** — это сервис для детекции и классификации **опор линий электропередачи (ЛЭП)** нацеленная на предотвращение различий между фактическими опорами ЛЭП и теми, что задокументированы.
Наша система ориентирована на распознавание изображений, на которых находятся ЛЭП.

## 🎯 Цель проекта

Цель проекта — разработка сервиса SafeGuard для детекции и классификации опор ЛЭП на изображениях, направленного на предотвращение расхождений между фактическими опорами ЛЭП и задокументированными.

## 🛠️ Технологии

Наш стек технологий включает:

- **ML**: 
  -   OpenAI CLIP
  -   ChromaDB
  -   OpenCV2
  -   PyTorch
  -   YOLOv11x
  -   Hugging Face
- **Backend**:
    - MinIO
    - VK Cloud S3
    - FastAPI
    - PostgreSQL
    - Docker, Docker Compose
- **Frontend**:
    - React 
    - Mobx 
    - Vite 
    - TypeScript 
    - Yarn 
    - Chakra UI 
    - FSD (Feature-Sliced Design) 

## 📦 Установка и запуск

Для развертывания проекта требуется Docker. Убедитесь, что у вас установлены Docker и Docker Compose.

1. Склонируйте репозиторий:

2. Запустите проект с помощью Docker Compose:
```bash
cp .env.example .env
docker build --output=nginx/dist frontend
docker compose up --build -d
```

3. Перейдите по ссылке для тестирования [Демо-версия](https://lap.lab260.ru).

## 📊 Метрики и результаты

Для оценки качества работы системы использовались метрики: **mAP**,**mAP@50**,**mAP@75**.

## Датасеты:
- TTPLA
- [собраный для детекции](https://hb.ru-msk.vkcloud-storage.ru/fits/dataset_detection.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=m3KNiQmw9Pfykv3nfBcHyx%2F20241201%2Fru-msk%2Fs3%2Faws4_request&X-Amz-Date=20241201T165601Z&X-Amz-Expires=2591999&X-Amz-SignedHeaders=host&X-Amz-Signature=de9798da5e651ab813dc9bbbbbfb2611894ad6b879ee5e94fab1aa55e879c738)
- [собраный для детекции](https://hb.ru-msk.vkcloud-storage.ru/fits/dataset_classification.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=m3KNiQmw9Pfykv3nfBcHyx%2F20241201%2Fru-msk%2Fs3%2Faws4_request&X-Amz-Date=20241201T170545Z&X-Amz-Expires=259199&X-Amz-SignedHeaders=host&X-Amz-Signature=c36a18e1dd2da72d3cf6720b37a4fdf0d8bdba5de2b8e865e5442ee9978ffd16)