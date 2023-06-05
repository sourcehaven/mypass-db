from __future__ import annotations

from typing import Iterable

from tinydb.queries import QueryLike
from tinydb.table import Document

from mypass.db.tiny.vault import vault


def create(
        *,
        password: str = None,
        salt: str = None,
        name: str = None,
        username: str = None,
        email: str = None,
        site: str = None,
        **kwargs
) -> int:
    """
    Creates a new document in the TinyDB database.

    Args:
        password (str, optional): The password value. Defaults to None.
        salt (str, optional): The salt value. Defaults to None.
        name (str, optional): The name value. Defaults to None.
        username (str, optional): The username value. Defaults to None.
        email (str, optional): The email value. Defaults to None.
        site (str, optional): The site value. Defaults to None.
        **kwargs: Additional key-value pairs representing document fields.

    Returns:
        int: The ID of the created document.

    Example usage:
        create(name="John Doe", username="johndoe", email="johndoe@example.com")
    """

    with vault() as v:
        return v.insert(
            dict(name=name, password=password, salt=salt, username=username, email=email, site=site, **kwargs))


def read(cond: QueryLike = None) -> list[Document]:
    """
    Retrieves documents from the password vault based on the provided condition.

    Args:
        cond (QueryLike, optional): A condition to filter the documents to retrieve. Defaults to None.

    Returns:
        list: A list of documents matching the provided condition.

    Example:
        - read()  # Retrieves all documents from the vault database
        - read(cond=where('name') == 'work')  # Retrieves documents with 'name' field equal to 'work'
    """

    with vault() as v:
        if cond is None:
            return v.all()

        return v.search(cond=cond)


def update(
        cond: QueryLike | None = None,
        doc_ids: Iterable[int] | None = None,
        password: str = None,
        salt: str = None,
        username: str = None,
        name: str = None,
        email: str = None,
        site: str = None,
        **kwargs
) -> list[int]:
    """
    Update records in the vault database.

    Args:
        cond (QueryLike | None, optional): A query-like object representing the condition for selecting records to update.
            Defaults to None.
        doc_ids (Iterable[int] | None, optional): An iterable of document IDs to specify the specific records to update.
            Defaults to None.
        password (str, optional): The updated password value. Defaults to None.
        salt (str, optional): The updated salt value. Defaults to None.
        username (str, optional): The updated username value. Defaults to None.
        name (str, optional): The updated name value. Defaults to None.
        email (str, optional): The updated email value. Defaults to None.
        site (str, optional): The updated site value. Defaults to None.
        **kwargs: Additional keyword arguments can be used to update other fields.

    Returns:
        Any: The result of the update operation.

    Raises:
        Any: Any exceptions raised during the update operation.

    Example:
        update(cond=where('site') == 'example.com', password='new_password', username='new_username')
    """
    d = {}
    if name is not None:
        d['name'] = name

    if password is not None:
        d['password'] = password

    if salt is not None:
        d['salt'] = salt

    if username is not None:
        d['username'] = username

    if email is not None:
        d['email'] = email

    if site is not None:
        d['site'] = site

    d.update(kwargs)

    with vault() as v:
        return v.update(fields=d, cond=cond, doc_ids=doc_ids)


def delete(cond: QueryLike | None = None, doc_ids: Iterable[int] | None = None) -> list[int]:
    """
    Deletes documents from the vault database based on the provided condition or document IDs.

    Args:
        cond (QueryLike | None, optional): A condition to filter the documents to delete. Defaults to None.
        doc_ids (Iterable[int] | None, optional): An iterable of document IDs to delete. Defaults to None.

    Returns:
        int: The number of documents deleted.

    Example:
        - delete(cond=where('name') == 'gmail')  # Deletes documents with 'name' field equal to 'gmail'
        - delete(doc_ids=[1, 3, 5])  # Deletes documents with IDs 1, 3, and 5

    Note:
        - If both `cond` and `doc_ids` are None, no documents will be deleted.
        - If `cond` and `doc_ids` are both provided, the deletion will be performed based on the combined criteria.
    """
    with vault() as v:
        return v.remove(cond=cond, doc_ids=doc_ids)
