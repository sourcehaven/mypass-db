class DbError(RuntimeError):
    pass


class MasterPasswordExistsError(DbError):
    pass


class MultipleMasterPasswordsError(DbError):
    pass


class EmptyRecordInsertionError(DbError):
    pass


class UserNotExistsError(DbError):
    pass
