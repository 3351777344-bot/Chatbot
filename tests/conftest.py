"""跨存储后端的测试夹具。"""

import pytest_asyncio

from storage.file_backend import FileBackend
from storage.sqlite_backend import SQLiteBackend


@pytest_asyncio.fixture(params=["sqlite", "file"])
async def backend(request, tmp_path):
    instance = (
        SQLiteBackend(str(tmp_path / "test.db"))
        if request.param == "sqlite"
        else FileBackend(str(tmp_path / "files"))
    )
    await instance.initialize()
    try:
        yield instance
    finally:
        await instance.close()
