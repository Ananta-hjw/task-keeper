# task-keeper

개인 할 일을 관리하는 작은 웹 API입니다. 책 3장의 스킬 실습용 예제 저장소입니다.

- 스택: Python, FastAPI, SQLAlchemy, SQLite
- 패키지 관리: uv
- 기본 브랜치: main

## 구조

```
task-keeper/
├── app/
│   ├── main.py              # FastAPI 앱과 엔드포인트
│   ├── database.py          # 엔진, 세션, Base
│   ├── models.py            # Task, Tag (다대다)
│   ├── schemas.py           # 응답/요청 스키마
│   └── services/
│       └── task_service.py  # list_tasks() (selectinload로 태그 일괄 로딩)
├── scripts/
│   └── seed.py              # 데모 데이터 생성
├── tests/
│   ├── conftest.py          # 메모리 DB, 테스트 클라이언트
│   └── test_smoke.py        # 기본 동작 확인
├── pyproject.toml          # 의존성과 프로젝트 메타데이터
└── uv.lock                 # 잠금 파일
```

## 실행

uv가 설치돼 있어야 합니다. 없으면 https://docs.astral.sh/uv/ 를 보고 설치하세요.

```
uv sync                              # 의존성 설치 + 가상환경 생성
uv run python scripts/seed.py        # 데모 할 일 100개 생성
uv run uvicorn app.main:app --reload
```

- API 문서: http://127.0.0.1:8000/docs
- 목록 조회: http://127.0.0.1:8000/tasks

## 엔드포인트

- `GET /tasks` 할 일 목록
- `POST /tasks` 할 일 생성. 본문 예: `{"title": "장보기", "tags": ["개인", "쇼핑"]}`
- `GET /tasks/{id}` 단건 조회

## 해결된 문제: 목록 조회 N+1

`app/services/task_service.py`의 `list_tasks()`는 원래 할 일을 한 번에 조회한 뒤, 응답을 직렬화할 때 각 할 일의 태그(`task.tags`)를 따로 조회했습니다. 할 일이 N개면 태그 조회 쿼리가 N번 더 실행되어, 할 일이 늘수록 `GET /tasks`가 느려지는 문제가 있었습니다.

`list_tasks()`의 쿼리에 `selectinload`를 적용해 태그를 한 번에 가져오도록 수정했습니다.

```python
from sqlalchemy.orm import selectinload

tasks = db.query(Task).options(selectinload(Task.tags)).all()
```

실제 실행되는 쿼리 수를 비교하려면 echo를 켜고 실행하세요.

```
SQLALCHEMY_ECHO=1 uv run uvicorn app.main:app
```

`GET /tasks`를 호출하면, 할 일 목록 SELECT 한 번과 태그 SELECT 한 번, 총 두 번만 실행되는 것을 콘솔에서 확인할 수 있습니다.

이 수정이 책 3.8 실습의 작업 내용입니다. 이슈 생성부터 커밋, PR, 리뷰, 리뷰 반영까지 다섯 스킬로 처리합니다.

## 테스트

```
uv run pytest
```
