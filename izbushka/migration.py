from typing import (
    Any,
    Protocol,
)


class Migration(Protocol):
    def run(self, client: Any) -> None:
        ...
