import asyncio
import errno
import datetime
import logging
import os
import socket
import sys

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as BaseCommand
from django.utils import autoreload
from django.utils.encoding import force_text

from aiodjango import get_aio_application


class Command(BaseCommand):

    def get_handler(self, *args, **options):
        wsgi = super().get_handler(*args, **options)
        return get_aio_application(wsgi=wsgi)

    def inner_run(self, *args, **options):
        # If an exception was silenced in ManagementUtility.execute in order
        # to be raised in the child process, raise it now.
        autoreload.raise_last_exception()

        shutdown_message = options.get('shutdown_message', '')
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'

        self.stdout.write("Performing system checks...\n\n")
        self.check(display_num_errors=True)
        self.check_migrations()
        now = datetime.datetime.now().strftime('%B %d, %Y - %X')
        self.stdout.write(now)
        self.stdout.write((
            "Django version %(version)s, using settings %(settings)r\n"
            "Starting aidjango server at http://%(addr)s:%(port)s/\n"
            "Quit the server with %(quit_command)s.\n"
        ) % {
            "version": self.get_version(),
            "settings": settings.SETTINGS_MODULE,
            "addr": '[%s]' % self.addr if self._raw_ipv6 else self.addr,
            "port": self.port,
            "quit_command": quit_command,
        })

        if options.get('use_reloader'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()
        app = self.get_handler(*args, **options)
        log = logging.getLogger('aiodjango.runserver')
        log.propagate = False
        log.setLevel(logging.INFO)
        stdout = logging.StreamHandler(stream=self.stdout)
        log.addHandler(stdout)
        handler = app.make_handler(access_log=log, access_log_format='%t "%r" %s %b %D')
        server = None
        try:
            server = loop.run_until_complete(
                loop.create_server(handler, self.addr, int(self.port)))
            loop.run_forever()
        except socket.error as e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            try:
                error_text = ERRORS[e.errno]
            except KeyError:
                error_text = force_text(e)
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)
        finally:
            loop.run_until_complete(handler.finish_connections(1.0))
            if server is not None:
                server.close()
                loop.run_until_complete(server.wait_closed())
            loop.run_until_complete(app.finish())
        loop.close()
