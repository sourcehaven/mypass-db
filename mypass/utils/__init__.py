# noinspection PyUnresolvedReferences
from mypass.db.tiny.vault import create as create_vault_password
from .master import create_master_password, read_master_password, update_master_password
from .vault import read_vault_passwords, update_vault_passwords, update_vault_password, \
    delete_vault_passwords, delete_vault_password
