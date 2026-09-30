from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

# 할 일과 태그는 다대다 관계입니다.
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # 기본 lazy 로딩(select). 목록을 만든 뒤 task마다 task.tags에 접근하면
    # 태그 조회 쿼리가 task 개수만큼 따로 실행됩니다(N+1).
    # list_tasks()는 selectinload로 이 문제를 피합니다.
    tags = relationship("Tag", secondary=task_tags, lazy="select")
