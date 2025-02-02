from sqlalchemy.orm.session import Session
import sqlalchemy as _sa

from .tables import User, Post, Comment

import pydantic as _p
import pytest


def test_as_pydantic_model():
    user_model = User.as_pydantic_model()
    assert user_model.__name__ == "Users"
    assert "id" in user_model.model_fields
    assert "name" in user_model.model_fields
    assert "age" in user_model.model_fields


def test_table_info():
    table_info = User.table_info()
    assert table_info.table_name == "users"
    assert "id" in table_info.primary_columns
    assert "age" in table_info.nullable_columns


def test_create_user(session: Session):
    user = User(id=1, name="John Doe", age=30)

    session.add(user)
    session.commit()

    assert user.id == 1
    assert user.name == "John Doe"
    assert user.age == 30


def test_create_user_without_age(session: Session):
    user = User(id=1, name="John Doe")

    session.add(user)
    session.commit()

    assert user.id == 1
    assert user.name == "John Doe"
    assert user.age is None


def test_invalid_user():
    user_model = User.as_pydantic_model()
    with pytest.raises(ValueError):
        user_model(id=1, name=None)


def test_update_user(session: Session):
    user = User(id=1, name="John Doe", age=30)
    session.add(user)
    session.commit()

    user.name = "Jane"
    session.commit()

    updated_user = session.query(User).filter_by(id=1).first()
    assert updated_user.name == "Jane"
    assert updated_user.age == 30


def test_delete_user(session: Session):
    user = User(id=1, name="John Doe", age=30)
    session.add(user)
    session.commit()

    assert session.query(User).filter_by(id=1).first() is not None

    session.delete(user)
    session.commit()

    deleted_user = session.query(User).filter_by(id=1).first()
    assert deleted_user is None


def test_query_user(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=2, name="Jane Doe", age=25)
    session.add_all([user1, user2])
    session.commit()

    users = session.query(User).all()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users


def test_user_age_nullable(session: Session):
    user = User(id=1, name="John Doe")
    session.add(user)
    session.commit()

    queried_user = session.query(User).filter_by(id=1).first()
    assert queried_user.age is None


def test_duplicate_user_id(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=1, name="Jane Doe", age=25)
    session.add(user1)
    session.commit()

    with pytest.raises(_sa.exc.IntegrityError):
        session.add(user2)
        session.commit()


def test_bulk_insert_users(session: Session):
    users = [
        User(id=1, name="John Doe", age=30),
        User(id=2, name="Jane Doe", age=25),
        User(id=3, name="Alice", age=28),
    ]
    session.bulk_save_objects(users)
    session.commit()

    queried_users = session.query(User).all()
    assert len(queried_users) == 3


def test_filter_users_by_age(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=2, name="Jane Doe", age=25)
    session.add_all([user1, user2])
    session.commit()

    users = session.query(User).filter(User.age > 26).all()
    assert len(users) == 1
    assert users[0].name == "John Doe"


def test_order_users_by_name(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=2, name="Jane Doe", age=25)
    session.add_all([user1, user2])
    session.commit()

    users = session.query(User).order_by(User.name).all()
    assert users[0].name == "Jane Doe"
    assert users[1].name == "John Doe"


def test_count_users(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=2, name="Jane Doe", age=25)
    session.add_all([user1, user2])
    session.commit()

    user_count = session.query(User).count()
    assert user_count == 2


def test_update_multiple_users(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=2, name="Jane Doe", age=25)
    session.add_all([user1, user2])
    session.commit()

    session.query(User).filter(User.age < 30).update({User.age: 26})
    session.commit()

    updated_users = session.query(User).filter(User.age == 26).all()
    assert len(updated_users) == 1
    assert updated_users[0].name == "Jane Doe"


def test_delete_multiple_users(session: Session):
    user1 = User(id=1, name="John Doe", age=30)
    user2 = User(id=2, name="Jane Doe", age=25)
    session.add_all([user1, user2])
    session.commit()

    session.query(User).filter(User.age < 30).delete()
    session.commit()

    remaining_users = session.query(User).all()
    assert len(remaining_users) == 1
    assert remaining_users[0].name == "John Doe"


def test_sqlalchemy_table_as_pydantic_model_serialization(session):
    user_model = User.as_pydantic_model()
    user = user_model(id=1, name="John Doe", age=30)
    user_dict = user.model_dump()
    assert user_dict["id"] == 1
    assert user_dict["name"] == "John Doe"
    assert user_dict["age"] == 30


def test_sqlalchemy_table_exclude_fields(session):
    user_model = User.as_pydantic_model(exclude=["age"])
    user = user_model(id=1, name="John Doe")
    user_dict = user.model_dump()
    assert "age" not in user_dict


def test_sqlalchemy_table_model_annotations(session):
    user_model = User.as_pydantic_model()
    assert user_model.model_fields["id"].annotation == int
    assert user_model.model_fields["name"].annotation == str
    assert user_model.model_fields["age"].annotation == int


def test_sqlalchemy_table_frozen_field(session):
    user_model = User.as_pydantic_model()
    user = user_model(id=1, name="John Doe", age=30)
    with pytest.raises(ValueError):
        user.id = 2


def test_sqlalchemy_table_custom_validators(session):
    @_p.field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        return value.upper()

    custom_user_model = User.as_pydantic_model(
        validators={"validate_name": validate_name}
    )
    user = custom_user_model(id=1, name="John Doe", age=30)
    assert user.name == "JOHN DOE"


def test_create_post(session: Session, user: User):
    post = Post(
        id=1, title="First Post", content="This is the first post", user_id=user.id
    )
    session.add(post)
    session.commit()

    assert post.id == 1
    assert post.title == "First Post"
    assert post.content == "This is the first post"
    assert post.user_id == user.id


def test_create_comment(session: Session, user: User, post: Post):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=user.id
    )
    session.execute(comment)
    session.commit()

    inserted_comment = session.query(Comment).filter_by(id=1).first()
    assert inserted_comment.id == 1
    assert inserted_comment.content == "Nice post!"
    assert inserted_comment.post_id == post.id
    assert inserted_comment.user_id == user.id


def test_query_post(session: Session, user: User):
    post1 = Post(
        id=1, title="First Post", content="This is the first post", user_id=user.id
    )
    post2 = Post(
        id=2, title="Second Post", content="This is the second post", user_id=user.id
    )
    session.add_all([post1, post2])
    session.commit()

    posts = session.query(Post).all()
    assert len(posts) == 2
    assert post1 in posts
    assert post2 in posts


def test_query_comment(session: Session, user: User, post: Post):
    comment1 = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=user.id
    )
    comment2 = Comment.insert().values(
        id=2, content="Great post!", post_id=post.id, user_id=user.id
    )
    session.execute(comment1)
    session.execute(comment2)
    session.commit()

    comments = session.query(Comment).all()
    assert len(comments) == 2
    assert comments[0].id == 1
    assert comments[1].id == 2


def test_update_post(session: Session, user: User):
    post = Post(
        id=1, title="First Post", content="This is the first post", user_id=user.id
    )
    session.add(post)
    session.commit()

    post.title = "Updated Post"
    session.commit()

    updated_post = session.query(Post).filter_by(id=1).first()
    assert updated_post.title == "Updated Post"


def test_update_comment(session: Session, user: User, post: Post):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=user.id
    )
    session.execute(comment)
    session.commit()

    session.execute(
        Comment.update().where(Comment.c.id == 1).values(content="Updated comment")
    )
    session.commit()

    updated_comment = session.query(Comment).filter_by(id=1).first()
    assert updated_comment.content == "Updated comment"


def test_delete_post(session: Session, user: User):
    post = Post(
        id=1, title="First Post", content="This is the first post", user_id=user.id
    )
    session.add(post)
    session.commit()

    session.delete(post)
    session.commit()

    deleted_post = session.query(Post).filter_by(id=1).first()
    assert deleted_post is None


def test_delete_comment(session: Session, user: User, post: Post):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=user.id
    )
    session.execute(comment)
    session.commit()

    session.execute(Comment.delete().where(Comment.c.id == 1))
    session.commit()

    deleted_comment = session.query(Comment).filter_by(id=1).first()
    assert deleted_comment is None


def test_comment_serialization():
    comment_model = Comment.as_pydantic_model()
    comment = comment_model(id=1, content="Nice post!", post_id=1, user_id=1)
    comment_dict = comment.model_dump()
    assert comment_dict["id"] == 1
    assert comment_dict["content"] == "Nice post!"
    assert comment_dict["post_id"] == 1
    assert comment_dict["user_id"] == 1


def test_post_serialization():
    post_model = Post.as_pydantic_model()
    post = post_model(
        id=1, title="First Post", content="This is the first post", user_id=1
    )
    post_dict = post.model_dump()
    assert post_dict["id"] == 1
    assert post_dict["title"] == "First Post"
    assert post_dict["content"] == "This is the first post"
    assert post_dict["user_id"] == 1


def test_post_exclude_fields():
    post_model = Post.as_pydantic_model(exclude=["content"])
    post = post_model(id=1, title="First Post", user_id=1)
    post_dict = post.model_dump()
    assert "content" not in post_dict


def test_comment_exclude_fields():
    comment_model = Comment.as_pydantic_model(exclude=["user_id"])
    comment = comment_model(id=1, content="Nice post!", post_id=1)
    comment_dict = comment.model_dump()
    assert "user_id" not in comment_dict


def test_post_model_annotations():
    post_model = Post.as_pydantic_model()
    assert post_model.model_fields["id"].annotation == int
    assert post_model.model_fields["title"].annotation == str
    assert post_model.model_fields["content"].annotation == str
    assert post_model.model_fields["user_id"].annotation == int


def test_comment_model_annotations():
    comment_model = Comment.as_pydantic_model()
    assert comment_model.model_fields["id"].annotation == int
    assert comment_model.model_fields["content"].annotation == str
    assert comment_model.model_fields["post_id"].annotation == int
    assert comment_model.model_fields["user_id"].annotation == int


def test_post_as_pydantic_model():
    post_model = Post.as_pydantic_model()
    assert post_model.__name__ == "Posts"
    assert "id" in post_model.model_fields
    assert "title" in post_model.model_fields
    assert "content" in post_model.model_fields
    assert "user_id" in post_model.model_fields


def test_comment_as_pydantic_model():
    comment_model = Comment.as_pydantic_model()
    assert comment_model.__name__ == "Comments"
    assert "id" in comment_model.model_fields
    assert "content" in comment_model.model_fields
    assert "post_id" in comment_model.model_fields
    assert "user_id" in comment_model.model_fields


def test_create_post_with_invalid_user_id(session: Session):
    post = Post(id=1, title="First Post", content="This is the first post", user_id=999)
    session.add(post)
    with pytest.raises(_sa.exc.IntegrityError):
        session.commit()


def test_create_comment_with_invalid_post_id(session: Session, user: User):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=999, user_id=user.id
    )
    with pytest.raises(_sa.exc.IntegrityError):
        session.execute(comment)


def test_create_comment_with_invalid_user_id(session: Session, post: Post):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=999
    )
    with pytest.raises(_sa.exc.IntegrityError):
        session.execute(comment)


def test_query_post_with_user(session: Session, user: User):
    post = Post(
        id=1, title="First Post", content="This is the first post", user_id=user.id
    )
    session.add(user)
    session.add(post)
    session.commit()

    queried_post = session.query(Post).filter_by(id=1).first()
    assert queried_post.user_id == user.id


def test_query_comment_with_post_and_user(session: Session, user: User, post: Post):
    comment = Comment.insert().values(
        id=1, content="Nice post!", post_id=post.id, user_id=user.id
    )
    session.add(user)
    session.add(post)
    session.execute(comment)
    session.commit()

    queried_comment = session.query(Comment).filter_by(id=1).first()
    assert queried_comment.post_id == post.id
    assert queried_comment.user_id == user.id
