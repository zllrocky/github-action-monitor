from datetime import datetime
from enum import Enum
from typing import Any
from sqlalchemy import DateTime, func, UniqueConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.core.db import Base


class WebhookDeliveryStatus(str, Enum):
    ACCEPTED = 'accepted'
    IGNORED = 'ignored'
    QUEUED = 'queued'
    DONE = 'done'
    FAILED = 'failed'


class JiraLinkStatus(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class DeliveryStepStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'


class DeliveryChannel(str, Enum):
    TELEGRAM = "telegram"
    JIRA = "jira"


class WebhookDelivery(Base):
    __tablename__ = 'webhook_deliveries'

    id: Mapped[int] = mapped_column(primary_key=True)
    github_delivery_id: Mapped[str] = mapped_column(unique=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  server_default=func.now())
    status: Mapped[WebhookDeliveryStatus] = mapped_column(
        String(32),
        default=WebhookDeliveryStatus.ACCEPTED)


class WorkflowRun(Base):
    __tablename__ = 'workflow_runs'

    id: Mapped[int] = mapped_column(primary_key=True)
    repository: Mapped[str]
    git_number: Mapped[int]
    __table_args__ = (UniqueConstraint('repository',
                                       'git_number',
                                       name='unique_repo_git_number'),
                      )
    workflow_name: Mapped[str]
    branch: Mapped[str]
    commit_sha: Mapped[str]
    status: Mapped[str | None]
    http_url: Mapped[str]


class JiraLink(Base):
    __tablename__ = 'jira_links'

    id: Mapped[int] = mapped_column(primary_key=True)
    repository: Mapped[str]
    workflow_name: Mapped[str]
    commit_sha: Mapped[str]
    __table_args__ = (UniqueConstraint('repository',
                                       'workflow_name',
                                       'commit_sha',
                                       name='unique_repo_flowname_sha'),
                      )
    key_jira: Mapped[str]
    status: Mapped[JiraLinkStatus] = mapped_column(String(32),
                                                   default=JiraLinkStatus.OPEN)


class DeliveryStep(Base):
    __tablename__ = 'delivery_steps'

    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_run_id: Mapped[int] = mapped_column(ForeignKey('workflow_runs.id'))
    channel: Mapped[DeliveryChannel] = mapped_column(String(32))
    __table_args__ = (UniqueConstraint('workflow_run_id',
                                       'channel',
                                       name='unique_launch_channel'),
                      )
    status: Mapped[DeliveryStepStatus] = mapped_column(
        String(32),
        default=DeliveryStepStatus.PENDING)
    attempt_counter: Mapped[int] = mapped_column(default=0)
    last_error_txt: Mapped[str | None]
