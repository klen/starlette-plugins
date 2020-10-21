__version__ = "0.0.6"
__license__ = "MIT"


import threading


setup_lock = threading.Lock()


class PluginException(Exception):
    pass


class PluginMiddleware:

    __slots__ = 'app',

    plugin = None

    def __init__(self, app):
        self.app = app

    def __call__(self, scope, receive, send) -> None:
        return self.plugin.process(scope, receive, send, app=self.app)


class PluginMeta(type):

    def __new__(mcs, name, bases, params):

        cls = super().__new__(mcs, name, bases, params)
        if bases and not cls.name:
            raise PluginException('Plugin `%s` doesn\'t have a name.' % cls)

        return cls


class StarlettePlugin(metaclass=PluginMeta):

    Exception = PluginException

    name = None
    config = {}

    middleware = on_startup = on_shutdown = None

    def __init__(self, app=None, **settings):
        self.app = app
        self.config.update(settings)
        if self.app:
            self.setup(app)

    def __call__(self, app, **settings):
        self.app = app

        # Setup plugins registry
        with setup_lock:
            if not hasattr(app, 'ps'):
                app.ps = type('Plugins', (object,), {})
            setattr(app.ps, self.name, self)

        # Prepare configuration
        self.config.update(settings)
        self.config = type('%sConfig' % self.name.title(), (object,), self.config)

        return type('%sMiddleware' % self.name.title(), (PluginMiddleware,), {'plugin': self})

    def setup(self, app, **settings):
        """Setup middlewares."""
        Middleware = self(app, **settings)

        self.app.add_middleware(Middleware)

    def process(self, scope, receive, send, app=None):
        """Process ASGI call."""
        app = app or self.app
        try:
            if scope['type'] == 'lifespan':
                return self.lifespan(scope, receive, send, app)

            return self.middleware(scope, receive, send, app)

        except Exception as exc:
            return self.exception(exc, scope, receive, send, app)

    def lifespan(self, scope, receive, send, app):
        """Process lifespan cycle."""

        async def reply_receive():
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await self.startup(scope)

            elif message['type'] == 'lifespan.shutdown':
                await self.shutdown(scope)

            return message

        return app(scope, reply_receive, send)

    async def middleware(self, scope, receive, send, app):
        """Default middleware."""
        return await app(scope, send, receive)

    async def startup(self, scope):
        """Default startup method."""
        pass

    async def shutdown(self, scope):
        """Default shutdown method."""
        pass

    def exception(self, exc, scope, receive, send, app):
        """Default exception."""
        raise exc
