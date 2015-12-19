import errno

from io import StringIO
from unittest.mock import patch

from django.test import TestCase

from aiodjango.management.commands.runserver import Command


class RunserverTestCase(TestCase):
    """Development server command options."""

    def setUp(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.cmd = Command(stdout=self.stdout, stderr=self.stderr)

    def assert_option(self, name, value):
        self.assertEqual(getattr(self.cmd, name), value)

    def assert_stderr(self, message):
        self.stderr.seek(0)
        self.assertIn(message, self.stderr.read())

    def test_default_options(self):
        """Deifault options for running the server."""
        with patch.object(self.cmd, 'run'):
            self.cmd.handle()
        self.assert_option('addr', '127.0.0.1')
        self.assert_option('port', '8000')
        self.assert_option('use_ipv6', None)

    def test_set_ip(self):
        """Run server on another IP address/port."""
        with patch.object(self.cmd, 'run'):
            self.cmd.handle(addrport='1.2.3.4:5000')
        self.assert_option('addr', '1.2.3.4')
        self.assert_option('port', '5000')
        self.assert_option('use_ipv6', None)

    @patch('asyncio.get_event_loop')
    def test_run(self, mock_loop):
        """Running the server should kick off the aiohttp app in the event loop."""
        self.cmd.handle()
        mock_loop.assert_called_with()
        mock_loop.return_value.run_forever.assert_called_with()

    @patch('asyncio.set_event_loop')
    @patch('asyncio.new_event_loop')
    def test_auto_reloader(self, mock_loop, mock_set_loop):
        """Running with the reloader thread creates a new event loop."""
        # Need to setup command options and use inner_run to prevent the
        # background thread from actually kicking off.
        self.cmd.addr = '127.0.0.1'
        self.cmd.port = '8000'
        self.cmd._raw_ipv6 = False
        self.cmd.inner_run(use_reloader=True)
        mock_loop.assert_called_with()
        mock_set_loop.assert_called_with(mock_loop.return_value)
        mock_loop.return_value.run_forever.assert_called_with()

    @patch('asyncio.get_event_loop')
    def test_handle_general_socket_errors(self, mock_loop):
        """Handle socket errors when createing the server."""
        mock_loop.return_value.create_server.side_effect = OSError('OS is broken')
        with patch('os._exit') as mock_exit:
            self.cmd.handle()
            mock_exit.assert_called_with(1)
        self.assert_stderr('OS is broken')

    @patch('asyncio.get_event_loop')
    def test_handle_known_socket_errors(self, mock_loop):
        """Special case socket errors for more meaningful error messages."""
        cases = (
            (errno.EACCES, 'You don\'t have permission to access that port.'),
            (errno.EADDRINUSE, 'That port is already in use.'),
            (errno.EADDRNOTAVAIL, 'That IP address can\'t be assigned to.'),
        )
        for number, message in cases:
            error = OSError()
            error.errno = number
            mock_loop.return_value.create_server.side_effect = error
            with patch('os._exit') as mock_exit:
                self.cmd.handle()
                mock_exit.assert_called_with(1)
            self.assert_stderr(message)

    @patch('asyncio.get_event_loop')
    def test_keyboard_stop(self, mock_loop):
        """User should be able to stop the server with a KeyboardInterrupt."""
        mock_loop.return_value.run_forever.side_effect = KeyboardInterrupt
        with self.assertRaises(SystemExit):
            self.cmd.handle()
