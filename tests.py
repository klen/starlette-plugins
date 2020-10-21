from unittest.mock import Mock

import pytest


@pytest.fixture
def app():
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse

    app = Starlette()

    @app.route('/')
    async def home(request):
        return PlainTextResponse('/')

    return app


@pytest.fixture
def client(app):
    from starlette.testclient import TestClient

    return TestClient(app)


def test_plugins(app, client):
    from starlette_plugins import StarlettePlugin

    check = Mock()

    class TestPlugin(StarlettePlugin):

        name = 'test'
        config = {'option2': True}

        async def middleware(self, scope, receive, send, app=None):
            check('middleware', self.name, scope['type'])
            return await app(scope, receive, send)

        async def startup(self, scope):
            check('lifespan', 'startup')

        async def shutdown(self, scope):
            check('lifespan', 'shutdown')

    test = TestPlugin()
    assert test

    test.setup(app, option1=42, option2=False)
    assert test.config.option1 == 42
    assert test.config.option2 is False

    assert app.ps
    assert app.ps.test is test

    with client:
        res = client.get('/')
        assert res.status_code == 200

        res = client.get('/')
        assert res.status_code == 200

    assert [args[0] for args in check.call_args_list] == [
        ('lifespan', 'startup'),
        ('middleware', 'test', 'http'),
        ('middleware', 'test', 'http'),
        ('lifespan', 'shutdown'),
    ]
