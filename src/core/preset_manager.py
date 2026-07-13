"""系统内置和用户自定义 Prompt 预设管理。"""

from pathlib import Path

import yaml

from models.schemas import Preset
from storage.base import StorageBackend

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PresetManager:
    BUILTIN_PRESETS_FILE = PROJECT_ROOT / "config" / "presets.yaml"

    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend

    async def load_builtin_presets(self) -> int:
        if not self.BUILTIN_PRESETS_FILE.exists():
            return 0
        with self.BUILTIN_PRESETS_FILE.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
        existing = {p.name for p in await self.backend.list_presets(0) if p.is_builtin}
        imported = 0
        for item in data.get("presets", []):
            name = str(item.get("name", "")).strip()
            prompt = str(item.get("system_prompt", "")).strip()
            if not name or not prompt or name in existing:
                continue
            await self.backend.save_preset(Preset(
                name=name,
                description=str(item.get("description", "")).strip(),
                system_prompt=prompt,
                is_builtin=True,
            ))
            existing.add(name)
            imported += 1
        return imported

    async def list_presets(self, user_id: int) -> list[Preset]:
        return await self.backend.list_presets(user_id)

    async def get_preset(self, preset_id: int) -> Preset | None:
        return await self.backend.get_preset_by_id(preset_id)

    async def create_preset(
        self, user_id: int, name: str, description: str, system_prompt: str
    ) -> Preset:
        name, system_prompt = name.strip(), system_prompt.strip()
        if not name:
            raise ValueError("预设名不能为空")
        if not system_prompt:
            raise ValueError("系统提示词不能为空")
        visible = await self.list_presets(user_id)
        if any(p.name == name for p in visible):
            raise ValueError(f"预设名 '{name}' 已存在")
        return await self.backend.save_preset(Preset(
            user_id=user_id,
            name=name,
            description=description.strip(),
            system_prompt=system_prompt,
        ))

    async def update_preset(
        self,
        preset: Preset,
        name: str,
        description: str,
        system_prompt: str,
        user_id: int | None = None,
    ) -> Preset:
        if preset.is_builtin:
            raise ValueError("内置预设不允许修改")
        if user_id is not None and preset.user_id != user_id:
            raise ValueError("无权修改其他用户的预设")
        name, system_prompt = name.strip(), system_prompt.strip()
        if not name or not system_prompt:
            raise ValueError("预设名和系统提示词不能为空")
        preset.name = name
        preset.description = description.strip()
        preset.system_prompt = system_prompt
        return await self.backend.save_preset(preset)

    async def delete_preset(self, preset_id: int, user_id: int | None = None) -> None:
        preset = await self.get_preset(preset_id)
        if preset is None:
            raise ValueError("预设不存在")
        if preset.is_builtin:
            raise ValueError("内置预设不允许删除")
        if user_id is not None and preset.user_id != user_id:
            raise ValueError("无权删除其他用户的预设")
        await self.backend.delete_preset(preset_id)
