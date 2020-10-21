__version__ = "0.0.2"
__license__ = "MIT"

import threading


setup_lock = threading.Lock()


class PluginException(Exception):
    pass


class PluginMiddleware:

    __slots__ = 'app',

    plugin = None

    def __init__(self, app, **kwargs):
        self.app = app

    def __call__(self, scope, receive, send) -> None:
        return self.plugin.middleware(self.app, scope, receive, send)


class PluginMeta(type):

    def __new__(mcs, name, bases, params):

        cls = super().__new__(mcs, name, bases, params)
        if bases and not cls.name:
            raise PluginException('Plugin `%s` doesn\'t have a name.' % cls)

        if cls.middleware:
            cls.__call__ = cls.middleware

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

    def setup(self, app, **settings):
        self.app = app

        # Setup plugins registry
        with setup_lock:
            if not hasattr(app, 'ps'):
                app.ps = type('Plugins', (object,), {})
            setattr(app.ps, self.name, self)

        # Prepare configuration
        self.config.update(settings)
        self.config = type('%sConfig' % self.name.title(), (object,), self.config)

        # Setup middlewares
        if self.middleware:
            Middleware = type(
                '%sMiddleware' % self.name.title(), (PluginMiddleware,), {'plugin': self})
            self.app.add_middleware(Middleware, plugin=self)

        # Setup events
        if self.on_startup:
            self.app.add_event_handler('startup', self.on_startup)

        if self.on_shutdown:
            self.app.add_event_handler('shutdown', self.on_shutdown)

        if self.on_shutdown:
            self.app.add_event_handler('shutdown', self.on_shutdown)

    # TODO
    def on_exception(self, exception_class_or_status_code):
        pass
