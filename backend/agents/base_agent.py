"""Abstract base class for all CASA agents."""
from abc import ABC, abstractmethod
from backend.core.audit_log import log_event


class BaseAgent(ABC):
    """Base class providing common agent infrastructure."""

    agent_name: str = "base"

    def audit(self, application_id: str, action: str, details: dict | None = None):
        """Write to the immutable audit log."""
        log_event(application_id, self.agent_name, action, details)

    @abstractmethod
    async def process(self, application_id: str, **kwargs) -> dict:
        """Execute the agent's primary task. Must be implemented by subclasses."""
        ...
