from abc import ABC, abstractmethod


class AlertNotifier(ABC):
    @abstractmethod
    def send(self, to_email: str, subject: str, body: str) -> None: ...
