import pytest
from click.testing import CliRunner
from migrate.common.types import DictData, alternative_name
from dataclasses import asdict, dataclass, field


def test_DictData_load_no_fields():
    @dataclass
    class SimpleTest(DictData):
        a: str
        b: int

    settings = SimpleTest.from_dict({"a": "123", "b": 456})
    assert settings.a == "123"
    assert settings.b == 456


def test_DictData_no_dataclass_exception():
    class SimpleTest(DictData):
        a: str
        b: int

    with pytest.raises(TypeError):
        settings = SimpleTest.from_dict({"a": "123", "b": 456})


def test_DictData_with_map():
    @dataclass
    class SimpleTest(DictData):
        a: str = field(metadata=alternative_name("c"))
        b: int

    settings = SimpleTest.from_dict({"c": "123", "b": 456})
    assert settings.a == "123"
    assert settings.b == 456


def test_DictData_with_bad_map_on_required_field():
    @dataclass
    class SimpleTest(DictData):
        a: str = field(metadata=alternative_name("c"))
        b: int

    with pytest.raises(TypeError):
        settings = SimpleTest.from_dict({"d": "123", "b": 456})


def test_DictData_with_converter_and_map():
    def do_convert(value):
        return str(value) + "!!"

    @dataclass
    class SimpleTest(DictData):
        a: str = field(metadata=alternative_name("c", converter=do_convert))
        b: int

    settings = SimpleTest.from_dict({"c": "123", "b": 456})
    assert settings.a == "123!!"
    assert settings.b == 456


def test_DictData_with_converter_no_map():
    # Converters only applied for alternative names
    with pytest.raises(TypeError):

        def do_convert(value):
            return str(value) + "!!"

        @dataclass
        class SimpleTest(DictData):
            a: str = field(metadata=alternative_name(converter=do_convert))
            b: int


def test_DictData_with_converter_no_map_lambda():
    # Converters only applied for alternative names
    with pytest.raises(TypeError):

        @dataclass
        class SimpleTest(DictData):
            a: str = field(
                metadata=alternative_name(converter=lambda value: str(value) + "!!")
            )
            b: int


def test_DictData_load_no_fields_serializes():
    @dataclass
    class SimpleTest(DictData):
        a: str
        b: int

    d = {"a": "123", "b": 456}
    settings = SimpleTest.from_dict(d)
    assert asdict(settings) == d


def test_DictData_with_map_serializes():
    @dataclass
    class SimpleTest(DictData):
        a: str = field(metadata=alternative_name("c"))
        b: int

    settings = SimpleTest.from_dict({"c": "123", "b": 456})
    assert asdict(settings) == {"a": "123", "b": 456}


def test_DictData_with_converter_and_map_serializes():
    def do_convert(value):
        return str(value) + "!!"

    @dataclass
    class SimpleTest(DictData):
        a: str = field(metadata=alternative_name("c", converter=do_convert))
        b: int

    settings = SimpleTest.from_dict({"c": "123", "b": 456})
    assert asdict(settings) == {"a": "123!!", "b": 456}


def test_DictData_with_converter_no_map_serializes():
    def do_convert(value):
        return str(value) + "!!"

    # Converters only applied for alternative names
    with pytest.raises(TypeError):

        @dataclass
        class SimpleTest(DictData):
            a: str = field(metadata=alternative_name(converter=do_convert))
            b: int


def test_DictData_with_converter_no_map_lambda_serializes():
    # Converters only applied for alternative names
    with pytest.raises(TypeError):

        @dataclass
        class SimpleTest(DictData):
            a: str = field(
                metadata=alternative_name(converter=lambda value: str(value) + "!!")
            )
            b: int
