import sqlalchemy.orm

from contextlib import contextmanager


class sessionmaker(sqlalchemy.orm.sessionmaker):
    def __call__(self, *args, **kw):
        session = super(sessionmaker, self).__call__(*args, **kw)
        session.rollback()  # it starts with an open transaction apparently ??
        return TransactionOnlySession(session)

    def object_session(self):
        raise Exception("object_session not supported")


class TransactionOnlySession(object):
    def __init__(self, session):
        self._session = session
        self._in_transaction = False

    @contextmanager
    def transaction(self):
        # There's always a transaction (begin() is only for autocommit mode)
        self.in_transaction = True
        try:
            yield SessionInTransaction(self._session)
        except:
            self._session.rollback()
            raise
        else:
            self._session.commit()
        finally:
            self.in_transaction = False


class SessionInTransaction(object):
    def __init__(self, session):
        self._session = session

    def add(self, *args, **kw): return self._session.add(*args, **kw)
    def add_all(self, *args, **kw): return self._session.add_all(*args, **kw)
    def bulk_insert_mappings(self, *args, **kw): return self._session.bulk_insert_mappings(*args, **kw)
    def bulk_save_objects(self, *args, **kw): return self._session.bulk_save_objects(*args, **kw)
    def bulk_update_mappings(self, *args, **kw): return self._session.bulk_update_mappings(*args, **kw)
    def delete(self, *args, **kw): return self._session.delete(*args, **kw)
    def execute(self, *args, **kw): return self._session.execute(*args, **kw)
    def query(self, *args, **kw): return self._session.query(*args, **kw)
    def scalar(self, *args, **kw): return self._session.scalar(*args, **kw)
