from pydantic import BaseModel


class BaseStatus(BaseModel):
    status: str


class HealthStatus(BaseStatus):
    pass


class ReadyStatus(BaseStatus):
    pass
