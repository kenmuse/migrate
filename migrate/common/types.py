"""Common base types used in the migration tool."""

from dataclasses import dataclass, field, fields, asdict
from enum import Enum, auto, unique
from typing import Callable, Any
import json


FieldConverter = Callable[[Any], Any]
"""A function that converts one value to another"""


def alternative_name(key: str, converter: FieldConverter = None):
    """Creates metadata with an alternative name and optional converter for a field."""
    return {"_base_settings": {"key": key, "converter": converter}}


class DictData:
    """Base class for composing dataclasses from a dictionary of settings."""

    @classmethod
    def _apply_alternative_field_names(cls, init_fields, field_names):
        """Finds alternative field names and adds them to the field_names dictionary"""
        for f in init_fields:
            alt_name = cls._get_mapped_alternative_name(f)
            if alt_name:
                field_names[alt_name] = (
                    [f.name]
                    if alt_name not in field_names
                    else field_names[alt_name] + [f.name]
                )

    @staticmethod
    def _get_mapped_alternative_name(f):
        """Returns the mapped alternative name for a field"""
        return f.metadata.get("_base_settings", {}).get("key", None)

    @staticmethod
    def _get_mapped_converter(f):
        """Returns the mapped converter for a field"""
        return f.metadata.get("_base_settings", {}).get("converter", None)

    @classmethod
    def _convert_value(cls, f, value):
        """Applies any mapped converteres"""
        if f:
            converter = cls._get_mapped_converter(f)
            if converter:
                return converter(value)
        return value

    @classmethod
    def from_dict(cls, settings: dict):
        init_fields = [f for f in fields(cls) if f.init]
        field_names = {f.name: [f.name] for f in init_fields}
        cls._apply_alternative_field_names(init_fields, field_names)
        filteredArgDict = cls._extract_class_dict(settings, init_fields, field_names)
        return cls(**filteredArgDict)

    @classmethod
    def _extract_class_dict(cls, settings, init_fields, field_names):
        def resolve_value(field_name, value):
            """Returns the converted value for the specified field name"""

            def find_field_by_name(field_name, init_fields):
                """Returns the field with the specified name"""
                return next(
                    iter(f for f in filter(lambda f: (f.name == field_name), init_fields))
                )

            return cls._convert_value(
                find_field_by_name(field_name, init_fields),
                value,
            )

        return {
            field_name: v if field_name == k else resolve_value(field_name, v)
            for k, v in settings.items()
            if k in field_names.keys()
            for field_name in field_names[k]
        }

    def to_dict(self):
        return asdict(self)

    def update(self, settings: dict):
        """Creates a copy of the object with the specified settings updated."""
        return self.from_dict({**self.to_dict(), **settings})


class SerializedEnum(Enum):
    """Base class for enumerations"""

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, val: str):
        """Converts a string to the appropriate enumeration value"""
        return cls[val.upper()]
