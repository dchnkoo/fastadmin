import pydantic.dataclasses as dataclasses
import pydantic.fields as _pf
import pydantic as _p

import pydantic_core as _pc

from sqlalchemy.sql.base import ReadOnlyColumnCollection
import sqlalchemy as _sa

import typing as _t


class FastAdminTable(_sa.Table):
    
    cache_pydantic_models: _t.ClassVar[bool] = False

    if _t.TYPE_CHECKING:
        __table_name__: str
        __table_info__: "TableInfo[_t.table]" | None
        __pydantic_model__: type[_p.BaseModel] | None

    @classmethod
    def _new(cls, *args, **kwds):
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
    def columns(self) -> ReadOnlyColumnCollection[str, "FastAdminColumn[_t.Any]"]:
        return super(FastAdminTable, self).columns
    
    def as_pydantic_model(
        self,
        config: _p.ConfigDict | None = None,
        doc: str | None = None,
        base: None = None,
        module: str = __name__,
        validators: dict[str, _t.Callable[[_t.Any], _t.Any]] | None = None, # type: ignore
        cls_kwargs: dict[str, _t.Any] | None = None,
    ):
        if self.cache_pydantic_models and self.__pydantic_model__ is not None:
            return self.__pydantic_model__

        define_columns = {
            column.name: (column.type.python_type, column.as_pydanitc_field()) 
            for column in self.columns
        }
        model = _p.create_model(
            self.__table_name__,
            __config__=config,
            __doc__=doc,
            __base__=base,
            __module__=module,
            __validators__=validators,
            __cls_kwargs__=cls_kwargs,
            **define_columns
        )

        if self.cache_pydantic_models:
            self.__pydantic_model__ = model
        return model

    @staticmethod
    def _proccess_columns(*args: _sa.Column) -> list["FastAdminColumn"]:
        handled = []
        for column in args:
            if not isinstance(column, FastAdminColumn):
                column = FastAdminColumn(
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
                    **column.dialect_kwargs
                )
            handled.append(column)
        return handled

    def __fastadmin_metadata__(self) -> "TableInfo[_t.Self]":
        if self.__table_info__ is not None:
            return self.__table_info__
        
        info = TableInfo(table=self, table_name=self.__table_name__)
        for column in self.columns:
            pre_added = {column.name: column}
            if column.primary_key:
                info.primary_columns.update(pre_added)
            if column.default:
                info.default_columns.update(pre_added)
            if column.unique:
                info.unique_columns.update(pre_added)
            if column.index:
                info.index_columns.update(pre_added)
            if column.nullable:
                info.nullable_columns.update(pre_added)
        self.__table_info__ = info
        return info


_T = _t.TypeVar("_T")


class FastAdminColumn(_sa.Column):

    def __init__(
        self, 
        __name_pos = None, 
        __type_pos = None, 
        *args: _sa.sql.base.SchemaEventTarget,
        default_factory: _t.Callable[[], _T] | None = _pf._Unset,
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
        json_schema_extra: _pf.JsonDict | _t.Callable[[_pf.JsonDict], None] | None = _pf._Unset,
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
        union_mode: _t.Literal['smart', 'left_to_right'] = _pf._Unset,
        fail_fast: bool | None = _pf._Unset,
        pydantic_extra: dict | None = None,
        name = None, 
        type_ = None, 
        autoincrement = "auto", 
        default = _sa.sql.base._NoArg.NO_ARG, 
        doc = None, 
        key = None, 
        index = None, 
        unique = None, 
        info = None, 
        nullable = _sa.schema.SchemaConst.NULL_UNSPECIFIED, 
        onupdate = None, 
        primary_key = False, 
        server_default = None, 
        server_onupdate = None, 
        quote = None, 
        system = False, 
        comment = None, 
        insert_sentinel = False, 
        _omit_from_statements = False, 
        _proxies = None, 
        **dialect_kwargs
    ):
        super(FastAdminColumn, self).__init__(
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
            **dialect_kwargs
        )
        self.defaul_factory = default_factory
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

    def as_pydanitc_field(self):
        default = (
            self.default.arg 
            if self.default is not None 
            else _pc.PydanticUndefined
        )
        
        return _p.Field(
            default=default,
            default_factory=self.defaul_factory,
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


@dataclasses.dataclass(
    kw_only=True, 
    slots=True, 
    config={"arbitrary_types_allowed": True},
    frozen=True,
)
class TableInfo:
    table: FastAdminTable
    table_name: str
    primary_columns: dict[str, FastAdminColumn] = dataclasses.Field(default_factory=dict)
    default_columns: dict[str, FastAdminColumn] = dataclasses.Field(default_factory=dict)
    unique_columns: dict[str, FastAdminColumn] = dataclasses.Field(default_factory=dict)
    index_columns: dict[str, FastAdminColumn] = dataclasses.Field(default_factory=dict)
    nullable_columns: dict[str, FastAdminColumn] = dataclasses.Field(default_factory=dict)
