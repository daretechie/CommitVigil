from arq import ArqRedis

# Shared State Container
# Explicitly typed to avoid circular import issues in the rest of the app
state: dict[str, ArqRedis | None] = {"redis": None}
