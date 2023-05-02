from importlib import import_module
from typing import ClassVar

from typing_extensions import Self

from ._codegen import Codegen
from ._model import ClassDecl
from ._parser import parse


class Compiler:
    """pydantic to zod data model declarations compiler.

    Usage:
        Compiler().parse("my_pkg.models").to_zod()

    Allows some level of customization.
    """

    MODEL_RENAME_RULES: ClassVar[dict[str, str]] = {}
    """Rules for converting pydantic model names to zod names based on the model's fully
    qualified name:

        pkg.module.ModelName -> Model1
    """

    IGNORE_TYPES: ClassVar[set[str]] = set()
    """Fully qualified names of types to ignore when parsing.

    .e.g. `pkg1.module1.MyType` - say when `MyType` is a deeply nested
    complicated type that pydantic2zod is not capable of parsing, we can
    tell the parser to ignore parsing it and instead use `Any` type.
    """

    def __init__(self) -> None:
        self._codegen = Codegen(self.MODEL_RENAME_RULES, self._modify_models)
        self._pydantic_models: list[ClassDecl] = []

    def parse(self, module_name: str) -> Self:
        """Parse pydantic models from the given module."""
        m = import_module(module_name)
        self._pydantic_models = parse(m, self.IGNORE_TYPES)
        return self

    def to_zod(self) -> str:
        """Generate zod data model declarations."""
        return self._codegen.to_zod(self._pydantic_models)

    def _modify_models(self, pydantic_models: list[ClassDecl]) -> list[ClassDecl]:
        """Override in case you want to apply some transformations on models.

        e.g. remove default field values.
        """
        return pydantic_models
