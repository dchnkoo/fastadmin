from inspect import signature

import pydantic as p
import typing as _t


class FunctionArg(p.BaseModel):
    annotation: _t.Any
    name: str


class FuncInfo(p.BaseModel):
    name: str
    doc: _t.Optional[str]
    args: _t.List[FunctionArg]
    return_value: _t.Any


def get_info(func: _t.Callable) -> FuncInfo:
    info = signature(func)

    return FuncInfo(
        name=func.__name__,
        doc=func.__doc__,
        args=[
            FunctionArg(annotation=i.annotation, name=i.name)
            for i in info.parameters.values()
        ],
        return_value=info.return_annotation,
    )
