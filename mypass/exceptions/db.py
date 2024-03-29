class DbError(RuntimeError):
    pass


class InvalidUpdateError(DbError):
    pass


class MasterPasswordExistsError(DbError):
    pass


class MultipleMasterPasswordsError(DbError):
    pass


class EmptyRecordInsertionError(DbError):
    pass


class UserNotExistsError(DbError):
    pass


class EmptyQueryError(DbError):
    pass


class RecordNotFoundError(DbError):
    pass


class RequiresIdError(DbError):
    pass
