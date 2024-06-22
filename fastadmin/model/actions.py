from fastadmin.model.sqlmodel2pydantic import SQLModel2Pydantic

import typing as _t


class ModelActions(SQLModel2Pydantic):
    @classmethod
    def which_model(
        cls, model_type: _t.Literal["form", "edit_form", "admin", "repr"] = "repr"
    ):
        return super().which_model(model=cls, model_type=model_type)
