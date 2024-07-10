import sqlalchemy as sa

from fastadmin.utils.descriptor.clas import classproperty

from enum import Enum
import pydantic as p
import typing as _t


def prem_validator(cls, v):
    if isinstance(v, list):
        return v
    return [v]


class Permissions:
    @classproperty
    def form(cls):
        perm_enum = Enum(
            "Permissions", {k.replace(":", "_"): k for k in cls._permissions}, type=str
        )

        return {
            "exclude": ["id"],
            "fields": {
                "permissions": (_t.Optional[list[perm_enum]], p.Field(default=[]))
            },
            "validators": {
                "premissions_validator": p.field_validator(
                    "permissions", check_fields=False, mode="before"
                )(prem_validator)
            },
        }

    @classproperty
    def edit_form(cls):
        get_form: dict = cls.form

        return {
            "exclude": get_form["exclude"] + ["password"],
            "fields": {"permissions": get_form["fields"]["permissions"]},
            "validators": get_form["validators"],
        }

    is_admin = sa.Column(sa.Boolean, nullable=False, default=False)
    is_super = sa.Column(sa.Boolean, nullable=False, default=False)
    permissions = sa.Column(sa.ARRAY(sa.String), nullable=True, default=[])
