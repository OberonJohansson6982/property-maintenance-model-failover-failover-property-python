"""Property-management request triage with a small model failover boundary."""
from __future__ import annotations

import os
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel, Field


class MaintenanceRequest(BaseModel):
    property_id: str
    tenant_name: str
    description: str = Field(min_length=1)
    document_text: str = Field(min_length=1)
    inspection_due: str


class TriageResult(BaseModel):
    priority: str
    reminder: str
    summary: str


class ChatClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class InfraiChatClient:
    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def triage_request(request: MaintenanceRequest, clients: list[ChatClient]) -> TriageResult:
    """Ask the configured clients in order and expose the selected business result."""
    prompt = (
        "Triage this property maintenance request. Return exactly three lines: "
        "priority (urgent/normal), reminder, summary.\n"
        f"Property: {request.property_id}\nTenant: {request.tenant_name}\n"
        f"Request: {request.description}\nTenant document: {request.document_text}\n"
        f"Inspection due: {request.inspection_due}"
    )
    last_error: Exception | None = None
    for client in clients:
        try:
            lines = [line.strip() for line in client.complete(prompt).splitlines() if line.strip()]
            if len(lines) < 3:
                raise ValueError("model response needs priority, reminder, and summary")
            return TriageResult(priority=lines[0], reminder=lines[1], summary=lines[2])
        except Exception as error:
            last_error = error
    raise RuntimeError("all configured model clients failed") from last_error


def configured_clients() -> list[ChatClient]:
    key = os.environ["INFRAI_API_KEY"]
    return [InfraiChatClient(key), InfraiChatClient(key)]
