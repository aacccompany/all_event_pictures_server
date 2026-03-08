# แนวทางการทำ "อัปโหลดแล้วโชว์รูปเลย AI ค่อยตามมาทีหลัง"

- [x] Add status field to `models/image.py`
- [x] Update schemas in `schemas/image.py`
- [x] Create WebSocket `ConnectionManager` in `utils/websocket.py`
- [x] Autogenerate DB Migration and Upgrade Database (Waiting on User manual run)
- [x] Refactor `controllers/image.py` to add WebSocket endpoint
- [x] Refactor `services/image.py` to use `BackgroundTasks` and emit WebSocket events
