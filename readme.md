# MyPass Db project

This package should be installed to run the database service.

## Special db rules:

1. If record id is returned in some form, every api endpoint implementation
should return it under the special `_id` field. In case of multiple id return,
they should be returned under the special `_ids` field contained in a list.

2. Also, every special (hidden) item should start with an *underscore* `_` and be upper-cased.
For example, associating vault passwords with users,
are done with the help of a special `_UID` field,
which should not be updated, or returned from the queries.

3. When communicating with the db api, special variables should start with an *underscore* `_`.
If the api is able to, these variables will be handled differently, and most importantly, they will be removed
from the request parameters. For example to save a password under a specific user, you should pass `_uid`
as a request param, but this will not be saved directly! It will be extracted from the request and passed to
controller functions if they can handle such parameters.

4. Protected variables (which should be encrypted by the encryption service api)
should end with two underscores `__`. This naming convention will signal the encryption
api to decrypt those fields first, and only return afterward.
