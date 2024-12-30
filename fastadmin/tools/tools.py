import pydantic.dataclasses as dataclasses
import pydantic.fields as _pf
import pydantic as _p

import pydantic_core as _pc

from sqlalchemy.orm.interfaces import _AttributeOptions
from sqlalchemy.orm import (
    DeclarativeBase as _declarative,
    declared_attr,
    MappedColumn,
)
from sqlalchemy.sql.base import (
    ReadOnlyColumnCollection,
    DedupeColumnCollection,
)
from sqlalchemy.sql.schema import (
    _ServerDefaultArgument,
    _ServerOnUpdateArgument,
    SchemaConst,
)
from sqlalchemy.sql import sqltypes
import sqlalchemy as _sa

import typing as _t


class FastAdminTable(_sa.Table):  # type: ignore
    cache_pydantic_models: _t.ClassVar[bool] = False

    if _t.TYPE_CHECKING:
        __table_name__: str
        __table_info__: "TableInfo" | None
        __pydantic_model__: type[_p.BaseModel] | None
        _columns: DedupeColumnCollection["FastColumn[_t.Any]"]

    @classmethod
    def _new(cls, *args: _t.Any, **kwds: dict[str, _t.Any]) -> _t.Self:
        try:
            name, metadata, args = args[0], args[1], args[2:]
        except IndexError:
            raise TypeError(
                "Table() takes at least two positional-only "
                "arguments 'name' and 'metadata'"
            )
        columns = cls._proccess_columns(*args)
        table: FastAdminTable = super(FastAdminTable, cls)._new(
            name, metadata, *columns, **kwds
        )

        table.__table_name__ = name
        table.__table_info__ = None
        table.__pydantic_model__ = None

        return table

    @property
    def columns(self) -> ReadOnlyColumnCollection[str, "FastColumn[_t.Any]"]:
        return super(FastAdminTable, self).columns

    def as_pydantic_model(
        self,
        config: _p.ConfigDict | None = None,
        doc: str | None = None,
        base: type[_p.BaseModel] | None = None,
        module: str = __name__,
        validators: dict[str, _t.Callable[[_t.Any], _t.Any]] | None = None,
        cls_kwargs: dict[str, _t.Any] | None = None,
        exclude: list[str] = ...,  # type: ignore
    ) -> type[_p.BaseModel]:
        if self.cache_pydantic_models and self.__pydantic_model__ is not None:
            return self.__pydantic_model__

        exclude = [] if isinstance(exclude, list) is False else exclude
        define_columns = {
            name: (
                column.anotation or column.type.python_type,
                column.as_pydantic_field(),
            )
            for column in self.columns
            if (name := column.name) not in exclude
        }
        model = _p.create_model(
            self.__table_name__.title(),
            __config__=config,
            __doc__=doc,
            __base__=base,
            __module__=module,
            __validators__=validators,
            __cls_kwargs__=cls_kwargs,
            **define_columns,
        )

        if self.cache_pydantic_models:
            self.__pydantic_model__ = model
        return model

    @staticmethod
    def _proccess_columns(*args: _sa.Column) -> list["FastColumn[_t.Any]"]:
        handled = []
        for column in args:
            if not isinstance(column, FastColumn):
                column = FastColumn(
                    column.name,
                    column.type,
                    *column.constraints,
                    autoincrement=column.autoincrement,
                    default=column.default,
                    doc=column.doc,
                    key=column.key,
                    index=column.index,
                    unique=column.unique,
                    info=column.info,
                    nullable=column.nullable,
                    onupdate=column.onupdate,
                    primary_key=column.primary_key,
                    server_default=column.server_default,
                    server_onupdate=column.server_onupdate,
                    comment=column.comment,
                    insert_sentinel=column._insert_sentinel,
                    system=column.system,
                    _omit_from_statements=column._omit_from_statements,
                    _proxies=column._proxies,
                    **column.dialect_kwargs,
                )
            handled.append(column)
        return handled

    def __fastadmin_metadata__(self) -> "TableInfo":
        if self.__table_info__ is not None:
            return self.__table_info__

        info = TableInfo(table=self, table_name=self.__table_name__)  # type: ignore
        for column in self.columns:
            pre_added = {column.name: column}
            if column.primary_key is True:
                info.primary_columns.update(pre_added)
            if (
                column.default is not None
                or column.default_factory != _pc.PydanticUndefined
            ):
                info.default_columns.update(pre_added)
            if column.unique is True:
                info.unique_columns.update(pre_added)
            if column.index is True:
                info.index_columns.update(pre_added)
            if column.nullable is True:
                info.nullable_columns.update(pre_added)
            if len(column.foreign_keys) > 0:
                info.foregin_colummns.update(pre_added)
        self.__table_info__ = info
        return info


class FastColumn[_T](_sa.Column):
    inherit_cache = True

    def __init__(
        self,
        __name_pos: _t.Optional[
            _t.Union[str, sqltypes.TypeEngine[_T], _sa.sql.base.SchemaEventTarget]
        ] = None,
        __type_pos: _t.Optional[
            _t.Union[str, sqltypes.TypeEngine[_T], _sa.sql.base.SchemaEventTarget]
        ] = None,
        *args: _sa.sql.base.SchemaEventTarget,
        default_factory: _t.Callable[[], _T] | None = _pf._Unset,
        alias: str | None = _pf._Unset,
        validation_alias: str | _pf.AliasPath | _pf.AliasChoices | None = _pf._Unset,
        alias_priority: int | None = None,
        serialization_alias: str | None = _pf._Unset,
        title: str | None = _pf._Unset,
        anotation: type | None = None,
        field_title_generator: _t.Callable[[str, _pf.FieldInfo], str]
        | None = _pf._Unset,
        examples: list[_t.Any] | None = _pf._Unset,
        exclude: bool | None = _pf._Unset,
        discriminator: str | _p.types.Discriminator | None = _pf._Unset,
        deprecated: _pf.Deprecated | str | bool | None = _pf._Unset,
        json_schema_extra: _pf.JsonDict
        | _t.Callable[[_pf.JsonDict], None]
        | None = _pf._Unset,
        frozen: bool | None = _pf._Unset,
        validate_default: bool | None = _pf._Unset,
        repr: bool = _pf._Unset,
        init: bool | None = _pf._Unset,
        init_var: bool | None = _pf._Unset,
        kw_only: bool | None = _pf._Unset,
        pattern: str | _pf.typing.Pattern[str] | None = _pf._Unset,
        strict: bool | None = _pf._Unset,
        coerce_numbers_to_str: bool | None = _pf._Unset,
        gt: _pf.annotated_types.SupportsGt | None = _pf._Unset,
        ge: _pf.annotated_types.SupportsGe | None = _pf._Unset,
        lt: _pf.annotated_types.SupportsLt | None = _pf._Unset,
        le: _pf.annotated_types.SupportsLe | None = _pf._Unset,
        multiple_of: float | None = _pf._Unset,
        allow_inf_nan: bool | None = _pf._Unset,
        max_digits: int | None = _pf._Unset,
        decimal_places: int | None = _pf._Unset,
        min_length: int | None = _pf._Unset,
        max_length: int | None = _pf._Unset,
        union_mode: _t.Literal["smart", "left_to_right"] = _pf._Unset,
        fail_fast: bool | None = _pf._Unset,
        pydantic_extra: dict | None = None,  # type: ignore
        name: str | None = None,
        type_: sqltypes.TypeEngine[_T] | None = None,
        autoincrement: str = "auto",
        default: _t.Any | None = None,
        doc: str | None = None,
        key: str | None = None,
        index: bool | None = None,
        unique: bool | None = None,
        info: _sa.sql._typing._InfoType = None,
        nullable: _t.Optional[
            _t.Union[bool, _t.Literal[SchemaConst.NULL_UNSPECIFIED]]  # type: ignore
        ] = _sa.schema.SchemaConst.NULL_UNSPECIFIED,
        onupdate: _t.Any | None = None,
        primary_key: bool = False,
        server_default: _t.Optional[_ServerDefaultArgument] = None,
        server_onupdate: _t.Optional[_ServerDefaultArgument] = None,
        quote: bool | None = None,
        system: bool = False,
        comment: str | None = None,
        insert_sentinel: bool = False,
        _omit_from_statements: bool = False,
        _proxies: _t.Any | None = None,
        **dialect_kwargs: dict[str, _t.Any],
    ):
        super(FastColumn, self).__init__(
            __name_pos,
            __type_pos,
            *args,
            name=name,
            type_=type_,
            autoincrement=autoincrement,
            default=default,
            doc=doc,
            key=key,
            index=index,
            unique=unique,
            info=info,
            nullable=nullable,
            onupdate=onupdate,
            primary_key=primary_key,
            server_default=server_default,
            server_onupdate=server_onupdate,
            quote=quote,
            system=system,
            comment=comment,
            insert_sentinel=insert_sentinel,
            _omit_from_statements=_omit_from_statements,
            _proxies=_proxies,
            **dialect_kwargs,
        )
        self.default_factory = default_factory
        self.alias = alias
        self.alias_priority = alias_priority
        self.validation_alias = validation_alias
        self.serialization_alias = serialization_alias
        self.title = title
        self.field_title_generator = field_title_generator
        self.examples = examples
        self.exclude = exclude
        self.discriminator = discriminator
        self.deprecated = deprecated
        self.json_schema_extra = json_schema_extra
        self.frozen = frozen
        self.validate_default = validate_default
        self.repr = repr
        self.init = init
        self.init_var = init_var
        self.kw_only = kw_only
        self.pattern = pattern
        self.strict = strict
        self.coerce_numbers_to_str = coerce_numbers_to_str
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.multiple_of = multiple_of
        self.allow_inf_nan = allow_inf_nan
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.min_length = min_length
        self.max_length = max_length
        self.union_mode = union_mode
        self.fail_fast = fail_fast
        self.pydantic_extra = pydantic_extra or {}
        self.anotation = anotation

    def as_pydantic_field_info(self) -> _p.fields.FieldInfo:
        return _p.fields.FieldInfo(
            annotation=self.type.python_type,
            default_factory=self.default_factory,
            alias=self.alias,
            alias_priority=self.alias_priority,
            validation_alias=self.validation_alias,
            serialization_alias=self.serialization_alias,
            title=self.title,
            field_title_generator=self.field_title_generator,
            description=self.doc,
            examples=self.examples,
            exclude=self.exclude,
            gt=self.gt,
            ge=self.ge,
            lt=self.lt,
            le=self.le,
            multiple_of=self.multiple_of,
            strict=self.strict,
            max_length=self.max_length,
            pattern=self.pattern,
            allow_inf_nan=self.allow_inf_nan,
            max_digits=self.max_digits,
            decimal_places=self.decimal_places,
            union_mode=self.union_mode,
            discriminator=self.discriminator,
            deprecated=self.deprecated,
            json_schema_extra=self.json_schema_extra,
            frozen=self.frozen,
            validate_default=self.validate_default,
            repr=self.repr,
            init=self.init,
            init_var=self.init_var,
            kw_only=self.kw_only,
            coerce_numbers_to_str=self.coerce_numbers_to_str,
            fail_fast=self.fail_fast,
            default=self._handle_default(),
        )

    def as_pydantic_field(self) -> _t.Any:
        return _p.Field(
            default=self._handle_default(),
            default_factory=self.default_factory,
            alias=self.alias,
            alias_priority=self.alias_priority,
            validation_alias=self.validation_alias,
            serialization_alias=self.serialization_alias,
            title=self.title,
            field_title_generator=self.field_title_generator,
            description=self.doc,
            examples=self.examples,
            exclude=self.exclude,
            discriminator=self.discriminator,
            deprecated=self.deprecated,
            json_schema_extra=self.json_schema_extra,
            frozen=self.frozen,
            validate_default=self.validate_default,
            repr=self.repr,
            init=self.init,
            init_var=self.init_var,
            kw_only=self.kw_only,
            pattern=self.pattern,
            strict=self.strict,
            coerce_numbers_to_str=self.coerce_numbers_to_str,
            gt=self.gt,
            ge=self.ge,
            lt=self.lt,
            le=self.le,
            multiple_of=self.multiple_of,
            allow_inf_nan=self.allow_inf_nan,
            max_digits=self.max_digits,
            decimal_places=self.decimal_places,
            min_length=self.min_length,
            max_length=self.max_length,
            union_mode=self.union_mode,
            **self.pydantic_extra,
        )

    def _handle_default(self) -> _t.Any | _pc.PydanticUndefinedType:
        if self.default is not None:
            if hasattr(self.default, "arg"):
                return self.default.arg
            return self.default
        return _pc.PydanticUndefined


class FastMappedColumn[_T](MappedColumn):
    inherit_cache = True

    def __init__(
        self,
        *args,
        default: _t.Optional[_t.Any] = None,
        default_factory: _t.Union[
            _sa.sql.base._NoArg, _t.Callable[[], _T]
        ] = _sa.sql.base._NoArg.NO_ARG,
        alias: str | None = _pf._Unset,
        validation_alias: str | _pf.AliasPath | _pf.AliasChoices | None = _pf._Unset,
        alias_priority: int | None = None,
        serialization_alias: str | None = _pf._Unset,
        title: str | None = _pf._Unset,
        doc: _t.Optional[str] = None,
        field_title_generator: _t.Callable[[str, _pf.FieldInfo], str]
        | None = _pf._Unset,
        examples: list[_t.Any] | None = _pf._Unset,
        exclude: bool | None = _pf._Unset,
        discriminator: str | _p.types.Discriminator | None = _pf._Unset,
        deprecated: _pf.Deprecated | str | bool | None = _pf._Unset,
        json_schema_extra: _pf.JsonDict
        | _t.Callable[[_pf.JsonDict], None]
        | None = _pf._Unset,
        frozen: bool | None = _pf._Unset,
        validate_default: bool | None = _pf._Unset,
        repr: bool = _pf._Unset,
        init: bool | None = _pf._Unset,
        init_var: bool | None = _pf._Unset,
        anotation: type | None = None,
        kw_only: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,
        hash: _t.Union[_sa.sql.base._NoArg, bool, None] = _sa.sql.base._NoArg.NO_ARG,
        pattern: str | _pf.typing.Pattern[str] | None = _pf._Unset,
        strict: bool | None = _pf._Unset,
        coerce_numbers_to_str: bool | None = _pf._Unset,
        compare: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,
        gt: _pf.annotated_types.SupportsGt | None = _pf._Unset,
        ge: _pf.annotated_types.SupportsGe | None = _pf._Unset,
        lt: _pf.annotated_types.SupportsLt | None = _pf._Unset,
        le: _pf.annotated_types.SupportsLe | None = _pf._Unset,
        multiple_of: float | None = _pf._Unset,
        allow_inf_nan: bool | None = _pf._Unset,
        max_digits: int | None = _pf._Unset,
        decimal_places: int | None = _pf._Unset,
        min_length: int | None = _pf._Unset,
        max_length: int | None = _pf._Unset,
        union_mode: _t.Literal["smart", "left_to_right"] = _pf._Unset,
        fail_fast: bool | None = _pf._Unset,
        pydantic_extra: dict | None = None,
        **kw,
    ):
        super(FastMappedColumn, self).__init__(
            *args,
            attribute_options=_AttributeOptions(
                init, repr, default, default_factory, compare, kw_only, hash
            ),
            **kw,
        )
        self.column = FastAdminTable._proccess_columns(self.column)[0]

        self.column.default = default
        self.column.default_factory = (
            default_factory
            if default_factory != _sa.sql.base._NoArg.NO_ARG
            else _pf._Unset
        )
        self.column.alias = alias
        self.column.alias_priority = alias_priority
        self.column.validation_alias = validation_alias
        self.column.serialization_alias = serialization_alias
        self.column.title = title
        self.column.field_title_generator = field_title_generator
        self.column.examples = examples
        self.column.exclude = exclude
        self.column.discriminator = discriminator
        self.column.deprecated = deprecated
        self.column.json_schema_extra = json_schema_extra
        self.column.frozen = frozen
        self.column.validate_default = validate_default
        self.column.repr = repr if isinstance(repr, bool) else _pf._Unset
        self.column.init = init if isinstance(init, bool) else _pf._Unset
        self.column.init_var = init_var
        self.column.kw_only = kw_only if isinstance(kw_only, bool) else _pf._Unset
        self.column.pattern = pattern
        self.column.strict = strict
        self.column.coerce_numbers_to_str = coerce_numbers_to_str
        self.column.gt = gt
        self.column.ge = ge
        self.column.lt = lt
        self.column.le = le
        self.column.multiple_of = multiple_of
        self.column.allow_inf_nan = allow_inf_nan
        self.column.max_digits = max_digits
        self.column.decimal_places = decimal_places
        self.column.min_length = min_length
        self.column.max_length = max_length
        self.column.union_mode = union_mode
        self.column.fail_fast = fail_fast
        self.column.pydantic_extra = pydantic_extra or {}
        self.column.doc = doc
        self.column.anotation = anotation


@dataclasses.dataclass(
    kw_only=True,
    slots=True,
    config={"arbitrary_types_allowed": True},
    frozen=True,
)
class TableInfo:
    table: FastAdminTable
    table_name: str
    primary_columns: dict[str, FastColumn[_t.Any]] = dataclasses.Field(
        default_factory=dict
    )
    default_columns: dict[str, FastColumn[_t.Any]] = dataclasses.Field(
        default_factory=dict
    )
    unique_columns: dict[str, FastColumn[_t.Any]] = dataclasses.Field(
        default_factory=dict
    )
    index_columns: dict[str, FastColumn[_t.Any]] = dataclasses.Field(
        default_factory=dict
    )
    nullable_columns: dict[str, FastColumn[_t.Any]] = dataclasses.Field(
        default_factory=dict
    )
    foregin_colummns: dict[str, FastColumn[_t.Any]] = dataclasses.Field(
        default_factory=dict
    )


def fastadmin_mapped_column[_T](
    __name_pos: _t.Optional[
        _t.Union[str, sqltypes.TypeEngine[_T], _sa.sql.base.SchemaEventTarget]
    ] = None,
    __type_pos: _t.Optional[
        _t.Union[sqltypes.TypeEngine[_T], _sa.sql.base.SchemaEventTarget]
    ] = None,
    *args: _sa.sql.base.SchemaEventTarget,
    init: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,
    repr: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,  # noqa: A002
    default: _t.Optional[_t.Any] = None,
    default_factory: _t.Union[
        _sa.sql.base._NoArg, _t.Callable[[], _T]
    ] = _sa.sql.base._NoArg.NO_ARG,
    compare: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,
    kw_only: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,
    hash: _t.Union[_sa.sql.base._NoArg, bool, None] = _sa.sql.base._NoArg.NO_ARG,  # noqa: A002
    nullable: _t.Optional[
        _t.Union[bool, _t.Literal[SchemaConst.NULL_UNSPECIFIED]]  # type: ignore
    ] = SchemaConst.NULL_UNSPECIFIED,
    primary_key: _t.Optional[bool] = False,
    deferred: _t.Union[_sa.sql.base._NoArg, bool] = _sa.sql.base._NoArg.NO_ARG,
    deferred_group: _t.Optional[str] = None,
    deferred_raiseload: _t.Optional[bool] = None,
    use_existing_column: bool = False,
    name: _t.Optional[str] = None,
    type_: _t.Optional[sqltypes.TypeEngine[_T]] = None,
    autoincrement: _sa.sql._typing._AutoIncrementType = "auto",
    doc: _t.Optional[str] = None,
    key: _t.Optional[str] = None,
    index: _t.Optional[bool] = None,
    unique: _t.Optional[bool] = None,
    info: _t.Optional[_sa.sql._typing._InfoType] = None,
    onupdate: _t.Optional[_t.Any] = None,
    insert_default: _t.Optional[_t.Any] = _sa.sql.base._NoArg.NO_ARG,
    server_default: _t.Optional[_ServerDefaultArgument] = None,
    server_onupdate: _t.Optional[_ServerOnUpdateArgument] = None,
    active_history: bool = False,
    quote: _t.Optional[bool] = None,
    system: bool = False,
    comment: _t.Optional[str] = None,
    sort_order: _t.Union[_sa.sql.base._NoArg, int] = _sa.sql.base._NoArg.NO_ARG,
    alias: str | None = _pf._Unset,
    validation_alias: str | _pf.AliasPath | _pf.AliasChoices | None = _pf._Unset,
    alias_priority: int | None = None,
    serialization_alias: str | None = _pf._Unset,
    title: str | None = _pf._Unset,
    field_title_generator: _t.Callable[[str, _pf.FieldInfo], str] | None = _pf._Unset,
    examples: list[_t.Any] | None = _pf._Unset,
    exclude: bool | None = _pf._Unset,
    discriminator: str | _p.types.Discriminator | None = _pf._Unset,
    deprecated: _pf.Deprecated | str | bool | None = _pf._Unset,
    json_schema_extra: _pf.JsonDict
    | _t.Callable[[_pf.JsonDict], None]
    | None = _pf._Unset,
    frozen: bool | None = _pf._Unset,
    validate_default: bool | None = _pf._Unset,
    init_var: bool | None = _pf._Unset,
    pattern: str | _pf.typing.Pattern[str] | None = _pf._Unset,
    strict: bool | None = _pf._Unset,
    coerce_numbers_to_str: bool | None = _pf._Unset,
    gt: _pf.annotated_types.SupportsGt | None = _pf._Unset,
    ge: _pf.annotated_types.SupportsGe | None = _pf._Unset,
    lt: _pf.annotated_types.SupportsLt | None = _pf._Unset,
    le: _pf.annotated_types.SupportsLe | None = _pf._Unset,
    multiple_of: float | None = _pf._Unset,
    allow_inf_nan: bool | None = _pf._Unset,
    max_digits: int | None = _pf._Unset,
    decimal_places: int | None = _pf._Unset,
    min_length: int | None = _pf._Unset,
    max_length: int | None = _pf._Unset,
    union_mode: _t.Literal["smart", "left_to_right"] = _pf._Unset,
    fail_fast: bool | None = _pf._Unset,
    pydantic_extra: dict | None = None,  # type: ignore
    **kw: _t.Any,
):
    return FastMappedColumn(
        __name_pos,
        __type_pos,
        *args,
        init=init,
        repr=repr,
        default=default,
        default_factory=default_factory,
        compare=compare,
        kw_only=kw_only,
        hash=hash,
        nullable=nullable,
        primary_key=primary_key,
        deferred=deferred,
        deferred_group=deferred_group,
        deferred_raiseload=deferred_raiseload,
        use_existing_column=use_existing_column,
        name=name,
        type_=type_,
        autoincrement=autoincrement,
        doc=doc,
        key=key,
        index=index,
        unique=unique,
        info=info,
        onupdate=onupdate,
        insert_default=insert_default,
        server_default=server_default,
        server_onupdate=server_onupdate,
        active_history=active_history,
        quote=quote,
        system=system,
        comment=comment,
        sort_order=sort_order,
        alias=alias,
        validation_alias=validation_alias,
        alias_priority=alias_priority,
        serialization_alias=serialization_alias,
        title=title,
        field_title_generator=field_title_generator,
        examples=examples,
        exclude=exclude,
        discriminator=discriminator,
        deprecated=deprecated,
        json_schema_extra=json_schema_extra,
        frozen=frozen,
        validate_default=validate_default,
        init_var=init_var,
        pattern=pattern,
        strict=strict,
        coerce_numbers_to_str=coerce_numbers_to_str,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        union_mode=union_mode,
        fail_fast=fail_fast,
        pydantic_extra=pydantic_extra,
        **kw,
    )


class FastAdminBase(_declarative):  # type: ignore
    if _t.TYPE_CHECKING:
        __table__: FastAdminTable

    @declared_attr.directive
    def __table_cls__(cls) -> type[FastAdminTable]:
        return FastAdminTable

    @classmethod
    def as_pydantic_model(
        cls,
        config: _p.ConfigDict | None = None,
        doc: str | None = None,
        base: type[_p.BaseModel] | None = None,
        module: str = __name__,
        validators: dict[str, _t.Callable[[_t.Any], _t.Any]] | None = None,
        cls_kwargs: dict[str, _t.Any] | None = None,
        exclude: list[str] = ...,
    ):
        return cls.__table__.as_pydantic_model(
            config=config,
            doc=doc,
            base=base,
            module=module,
            validators=validators,
            cls_kwargs=cls_kwargs,
            exclude=exclude,
        )

    @classmethod
    def table_info(cls):
        return cls.__table__.__fastadmin_metadata__()
