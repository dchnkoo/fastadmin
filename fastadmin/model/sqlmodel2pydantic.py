from pydantic_core import PydanticUndefined
import pydantic as p

import typing as _t

from fastadmin.conf import FastAdminConfig
from fastadmin.utils import types as _tb
from fastadmin.ui import urls

if _t.TYPE_CHECKING:
    from fastadmin.metadata import MetaInfo, TableColumn, FastAdminMeta


exclude_fields: _t.TypeAlias = list[str]
fields_options: _t.TypeAlias = dict[str, _t.Any]
validators: _t.TypeAlias = dict[str, _t.Callable]


class SQLModel2Pydantic:
    @classmethod
    def which_model(
        cls: type["FastAdminMeta"],
        model: type["FastAdminMeta"],
        model_type: _tb.FastModels = "repr",
    ) -> p.BaseModel:
        config_dict: p.BaseModel | dict = getattr(model, model_type)

        if hasattr(config_dict, "__pydantic_root_model__"):
            return config_dict

        exclude, fields, valids, base = cls._parse_config(config=config_dict)

        metainfo = cls.__get_metainfo__(model.__tablename__)

        columns = cls._get_valid_columns(
            metainfo=metainfo, fields=fields, exclude=exclude
        )

        return cls.generate_pydantic_model(
            metainfo=metainfo,
            columns=columns,
            validators=valids,
            base=base,
        )

    @staticmethod
    def _parse_config(
        config: dict
    ) -> tuple[exclude_fields, fields_options, validators, p.BaseModel]:
        exclude = config.get("exclude", [])
        fields = config.get("fields", {})
        valids = config.get("validators", None)
        base = config.get("base", None)

        return (exclude, fields, valids, base)

    @staticmethod
    def _get_valid_columns(
        metainfo: "MetaInfo", fields: dict[str, _t.Any], exclude: list[str]
    ) -> dict[str, _t.Union[tuple[type, p.Field], "TableColumn"]]:
        fields_names = [name for name in fields.keys() if name not in exclude]
        meta_columns = [
            name
            for name in metainfo.columns.keys()
            if name not in fields_names and name not in exclude
        ]
        meta_columns.extend(fields_names)

        return {
            "custom_" + k if k in fields else k: fields.get(k)
            if k in fields
            else metainfo.columns.get(k)
            for k in meta_columns
        }

    @staticmethod
    def _set_pydantic_model_name(config: dict, metainfo: "MetaInfo"):
        config["__model_name"] = metainfo.table_class_name

    @classmethod
    def generate_pydantic_model(
        cls: type["FastAdminMeta"],
        metainfo: "MetaInfo",
        columns: dict[str, _t.Union[tuple[type, p.Field], "TableColumn"]],
        validators: dict[str, classmethod] | None,
        base: p.BaseModel | None,
    ) -> p.BaseModel:
        config_dict = {}

        cls._set_pydantic_model_name(config=config_dict, metainfo=metainfo)

        for name, options in columns.items():
            if name.startswith("custom_"):
                config_dict[name.removeprefix("custom_")] = options
                continue

            column_type = (
                _t.Optional[options.python_type]
                if options.nullable
                else options.python_type
            )
            column_field_config = p.Field(
                default=None
                if (options.nullable is True and options.default_value is None)
                else PydanticUndefined
                if options.default_value is None
                else options.default_value,
                title=options.doc,
                json_schema_extra={},
            )

            if options.foregin_key is not None:
                url = (
                    FastAdminConfig.api_path_strip
                    + FastAdminConfig.api_root_url
                    + urls.SEARCH.format(table=options.foregin_key.table_name)
                )

                column_field_config.json_schema_extra["search_url"] = url

            config_dict[name] = (column_type, column_field_config)

        return p.create_model(__base__=base, __validators__=validators, **config_dict)
