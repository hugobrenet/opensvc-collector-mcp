from contextvars import ContextVar, Token
from dataclasses import dataclass


@dataclass(frozen=True)
class CollectorCredentials:
    username: str
    password: str


_COLLECTOR_CREDENTIALS: ContextVar[CollectorCredentials | None] = ContextVar(
    "collector_credentials",
    default=None,
)


def set_collector_credentials(
    credentials: CollectorCredentials,
) -> Token[CollectorCredentials | None]:
    return _COLLECTOR_CREDENTIALS.set(credentials)


def reset_collector_credentials(token: Token[CollectorCredentials | None]) -> None:
    _COLLECTOR_CREDENTIALS.reset(token)


def get_collector_credentials() -> CollectorCredentials | None:
    return _COLLECTOR_CREDENTIALS.get()
