from fastui import components as c, events as e, types
import fastui.class_name as cls_name

from fastadmin.conf import FastAdminConfig

import pydantic as p
import typing as _t

if _t.TYPE_CHECKING:
    from fastadmin.metadata import FastAdminMeta


class FastAdminComponents:
    @classmethod
    def page_frame(
        cls,
        body: _t.List[c.AnyComponent],
        heading: _t.List[c.AnyComponent] = [],
        left: _t.List[c.AnyComponent] = [],
        right: _t.List[c.AnyComponent] = [],
        footer: _t.List[c.AnyComponent] = [],
    ) -> list[c.AnyComponent]:
        return [
            *heading,
            c.Div(
                components=[
                    *left,
                    c.Page(components=body),
                    *right,
                ],
                class_name="grid gap-4",
            ),
            *footer,
        ]

    @classmethod
    def header(
        cls: type["FastAdminMeta"],
        title: _t.Optional[str] = None,
        title_event: _t.Optional[e.AnyEvent] = None,
        start_links: _t.List[c.Link] = [],
        end_links: _t.List[c.Link] = [],
        class_name: cls_name.ClassNameField = None,
    ) -> list[c.AnyComponent]:
        end_links.append(
            c.Link(
                components=[
                    c.Button(
                        text="Logout",
                        on_click=e.PageEvent(name="exit"),
                        class_name="btn btn-danger",
                    )
                ],
            )
        )

        return [
            c.Navbar(
                title=title,
                title_event=title_event,
                start_links=start_links,
                end_links=end_links,
                class_name=class_name,
            )
        ]

    @classmethod
    def exit_event(cls: type["FastAdminMeta"]) -> list[c.AnyComponent]:
        return [
            c.Modal(
                title="Logout",
                body=[c.Text(text="Are you sure do you want to logout?")],
                open_trigger=e.PageEvent(name="exit"),
                footer=[
                    c.Button(
                        text="Cancel",
                        on_click=e.PageEvent(name="exit", clear=True),
                        named_style="secondary",
                    ),
                    c.Button(
                        text="Logout",
                        on_click=e.PageEvent(name="logout"),
                        class_name="btn btn-danger",
                    ),
                ],
            ),
            c.Form(
                submit_url=FastAdminConfig.api_root_url + cls._get_urls().EXIT,
                footer=[],
                submit_trigger=e.PageEvent(name="logout"),
                form_fields=[
                    c.FormFieldInput(
                        name="", title="", initial="data", html_type="hidden"
                    )
                ],
                class_name="",
            ),
        ]

    @classmethod
    def table_with_pagination(
        cls: type["FastAdminMeta"],
        page: int,
        total: int,
        data: _t.Sequence[p.SerializeAsAny[types.DataModel]],
        data_model: _t.Optional[type[p.BaseModel]] = None,
        class_name_table: c._class_name.ClassNameField = None,
        page_query_param: str = "page",
        class_name_pagination: c._class_name.ClassNameField = None,
    ) -> tuple[c.Table, c.Pagination]:
        return [
            c.Table(
                data=[data_model(**i) for i in data] if data_model else data,
                columns=cls.display_lookups,
                data_model=data_model,
                no_data_message=cls.no_data_message,
                class_name=class_name_table,
            ),
            c.Pagination(
                page=page,
                page_size=cls.table_size,
                total=total,
                page_query_param=page_query_param,
                class_name=class_name_pagination,
            ),
        ]
