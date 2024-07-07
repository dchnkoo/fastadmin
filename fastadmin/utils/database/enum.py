import sqlalchemy as sa


set_enum = lambda enum, name: sa.Enum(  # noqa E731
    enum,
    name=name,
    values_callable=lambda e: [field.value for field in e],
    create_type=False,
)
