# MyPass Db project

This package should be installed to run the database service.

## Special db rules:

If record id is returned in some form, every api endpoint implementation
should return it under the special `_id` field. In case of multiple id return,
they should be returned under the special `_ids` field contained in a list.

Also, every special (hidden) item should start with an *underscore* `_`.
For example, associating vault passwords with users,
are done with the help of a special `_user_id` field,
which should not be updated, or returned from the queries.
