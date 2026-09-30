from sqlalchemy import event


def test_create_and_list(client):
    res = client.post("/tasks", json={"title": "테스트 할 일", "tags": ["개인", "긴급"]})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "테스트 할 일"
    assert {t["name"] for t in body["tags"]} == {"개인", "긴급"}

    res = client.get("/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["tags"]


def test_list_tasks_query_count_is_constant(client, db_session):
    # list_tasks()가 selectinload로 태그를 한 번에 가져오는지 확인합니다.
    # N+1이면 할 일 개수만큼 태그 조회 쿼리가 늘어나 이 테스트가 실패합니다.
    for i in range(5):
        client.post("/tasks", json={"title": f"할 일 {i}", "tags": ["공통"]})

    engine = db_session.get_bind()
    query_count = 0

    def count_queries(*args, **kwargs):
        nonlocal query_count
        query_count += 1

    event.listen(engine, "before_cursor_execute", count_queries)
    try:
        res = client.get("/tasks")
    finally:
        event.remove(engine, "before_cursor_execute", count_queries)

    assert res.status_code == 200
    assert len(res.json()) == 5
    # 목록 SELECT 1번 + selectinload 태그 SELECT 1번 = 2번이어야 합니다.
    assert query_count <= 2
