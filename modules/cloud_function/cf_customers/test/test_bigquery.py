import io
import json
import types
import pytest
import logging
from unittest.mock import MagicMock, patch
from modules.cloud_function.cf_customers.src.utils.bigquery import BigQuery


class FakeLoadJob:
    def __init__(self, states, errors=None, output_rows=0):
        self._states = list(states)
        self.state = self._states[0] if self._states else 'DONE'
        self.errors = errors or []
        self.output_rows = output_rows

    def reload(self):
        if self._states:
            self._states.pop(0)
        self.state = self._states[0] if self._states else 'DONE'


class FakeBigQueryModule(types.SimpleNamespace):
    class LoadJobConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class SourceFormat:
        NEWLINE_DELIMITED_JSON = "NEWLINE_DELIMITED_JSON"

    class WriteDisposition:
        WRITE_APPEND = "WRITE_APPEND"

    class CreateDisposition:
        CREATE_NEVER = "CREATE_NEVER"

    class Client:
        def __init__(self, project=None):
            self.project = project
            self.load_table_from_file = MagicMock()
