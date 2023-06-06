class DbError(RuntimeError):
    pass


class MasterPasswordExistsError(DbError):
    pass


class MultipleMasterPasswordsError(DbError):
    pass
