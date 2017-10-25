from sqlalchemy.ext.declarative import declarative_base as decl_base


def declarative_base():
    """
    Returns an instance of ``sqlalchemy.ext.declarative.DeclarativeMeta``
    base class for declarative model definitions.

    :return sqlalchemy.ext.declarative.DeclarativeMeta: Declarative base class.
    """
    if not declarative_base.instance:
        declarative_base.instance = decl_base()
    return declarative_base.instance


# Set instance to None by default. This way it will be created when the factory
# function is called for the first time.
# This approach guarantees that only one instance of declarative base exists.
declarative_base.instance = None

# Create an instance of declarative base to use in models.
DeclarativeBase = declarative_base()
