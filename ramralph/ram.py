"""RAM data backend for Ralph."""

import logging
from typing import Iterator, Optional, Union

from pydantic import PositiveInt
from ralph.backends.data.base import (
    BaseDataBackend,
    BaseDataBackendSettings,
    DataBackendStatus,
)
from ralph.conf import BaseSettingsConfig
from ralph.exceptions import BackendParameterException

logger = logging.getLogger(__name__)


class RAMDataBackendSettings(BaseDataBackendSettings):
    """RAM data backend default configuration.

    Attributes:
        DEFAULT_COLLECTION (str): The name of the default collection.
        INCLUDE_DEMO_RECORDS (bool): Whether to include some demonstration records.
    """

    class Config(BaseSettingsConfig):
        """Pydantic Configuration."""

        env_prefix = "RALPH_BACKENDS__DATA__RAM__"

    DEFAULT_COLLECTION: str = "users"
    INCLUDE_DEMO_RECORDS: bool = True


class RAMDataBackend(BaseDataBackend[RAMDataBackendSettings, str]):
    """RAM data backend."""

    name = "ram"

    def __init__(self, settings: Optional[RAMDataBackendSettings] = None):
        """Instantiate the RAM data backend.

        Args:
            settings (LDPDataBackendSettings or None): The data backend settings.
                If `settings` is `None`, a default settings instance is used instead.
        """
        super().__init__(settings)
        self.data = {}
        if self.settings.INCLUDE_DEMO_RECORDS:
            self.data["users"] = [
                {"id": "1", "first_name": "John", "last_name": "Doe"},
                {"id": "2", "first_name": "Jane", "last_name": "Doe"},
            ]
            self.data["activities"] = [
                {"id": "1", "user": "1", "activity": "reading"},
                {"id": "2", "user": "2", "activity": "walking"},
            ]

    def status(self) -> DataBackendStatus:
        """Check whether the RAM is accessible."""
        # We assume that RAM is always accessible.
        return DataBackendStatus.OK

    def read(  # noqa: PLR0913
        self,
        query: Optional[str] = None,
        target: Optional[str] = None,
        chunk_size: Optional[int] = None,
        raw_output: bool = False,
        ignore_errors: bool = False,
        max_statements: Optional[PositiveInt] = None,
    ) -> Union[Iterator[bytes], Iterator[dict]]:
        """Read records matching the query from RAM and yield it.

        Args:
            query (str): The ID of the record to read.
            target (str or None): The target collection containing the records.
                If target is `None`, the `DEFAULT_COLLECTION` is used instead.
            chunk_size (int or None): The chunk size when reading records by batch.
                If `chunk_size` is `None` it defaults to `READ_CHUNK_SIZE`.
            raw_output (bool): Controls whether to yield bytes or dictionaries.
            ignore_errors (bool): No impact as no encoding operation is performed.
            max_statements (int): The maximum number of statements to yield.
                If `None` (default) or `0`, there is no maximum.

        Yield:
            dict: If `raw_output` is False.
            bytes: If `raw_output` is True.

        Raise:
            BackendException: If a failure occurs during LDP connection.
            BackendParameterException: If the `target` argument is not a collection.
        """
        yield from super().read(
            query, target, chunk_size, raw_output, ignore_errors, max_statements
        )

    def _read_dicts(
        self,
        query: str,
        target: Optional[str],
        chunk_size: int,  # noqa: ARG002
        ignore_errors: bool,  # noqa: ARG002
    ) -> Iterator[dict]:
        """Method called by `self.read` yielding dictionaries. See `self.read`."""
        if not target:
            target = self.settings.DEFAULT_COLLECTION

        if target not in self.data:
            raise BackendParameterException("Target collection doesn't exist.")

        if not query:
            yield from self.data[target]
        else:
            for record in self.data[target]:
                if record.get("id") == query:
                    yield record

    def close(self) -> None:
        """Cleanup RAM data backend."""
        self.data = {}
