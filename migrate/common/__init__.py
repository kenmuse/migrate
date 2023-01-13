from dataclasses import dataclass, field, fields
from enum import Enum, auto, unique


def alternative_name(key: str):
    return {"_base_settings": {"key": key}}


def _get_mapped_alternative_name(f):
    return f.metadata.get("_base_settings", {}).get("key", None)


class BaseDataclass:
    # company: str | None = field(default=None, metadata={"_name": "corp"})
    email: str | None = field(default=None)
    can_pub: bool = field(default=False, metadata=alternative_name("allow_all"))
    can_private: bool = field(default=False, metadata=alternative_name("allow_all"))
    location: str | None = None

    @classmethod
    def from_dict(cls, settings: dict):
        init_fields = [f for f in fields(cls) if f.init]
        field_names = {f.name: [f.name] for f in init_fields}
        for f in init_fields:
            alt_name = _get_mapped_alternative_name(f)
            if alt_name:
                field_names[alt_name] = (
                    [f.name]
                    if alt_name not in field_names
                    else field_names[alt_name] + [f.name]
                )
        filteredArgDict = {
            field_name: v
            for k, v in settings.items()
            if k in field_names.keys()
            for field_name in field_names[k]
        }
        return cls(**filteredArgDict)
