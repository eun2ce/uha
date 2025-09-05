from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware


class SessionMiddleware(StarletteSessionMiddleware):
    """Custom session middleware wrapper."""

    pass
