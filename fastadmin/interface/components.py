from fastui import components as c, events as e
import fastui.class_name as cls_name

import typing as _t


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
        cls,
        title: _t.Optional[str] = None,
        title_event: _t.Optional[e.AnyEvent] = None,
        start_links: _t.List[c.Link] = [],
        end_links: _t.List[c.Link] = [],
        class_name: cls_name.ClassNameField = None,
    ) -> list[c.AnyComponent]:
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
    def left(cls) -> list[c.AnyComponent]:
        return []

    @classmethod
    def right(cls) -> list[c.AnyComponent]:
        return []

    @classmethod
    def body(cls) -> list[c.AnyComponent]:
        return []

    @classmethod
    def footer(cls) -> list[c.AnyComponent]:
        return []
