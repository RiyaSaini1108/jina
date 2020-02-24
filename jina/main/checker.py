import os

from .. import __jina_env__
from ..helper import colored, yaml, import_classes
from ..logging import default_logger

if False:
    # fix type-hint complain for sphinx and flake
    import argparse


class ImportChecker:
    """Check all executors, drivers and handler functions in the package. """

    def __init__(self, args: 'argparse.Namespace'):
        default_logger.info('\navailable executors\n'.upper())
        import jina.executors
        import_classes(jina.executors.ExecutorType, jina.executors.__path__[0], show_import_table=True)

        default_logger.info('\navailable drivers\n'.upper())
        import jina.drivers
        import_classes(jina.drivers.DriverType, jina.drivers.__path__[0], show_import_table=True)

        # check available driver group

        default_logger.info('\navailable driver groups\n'.upper())
        from pkg_resources import resource_stream
        with resource_stream('jina', '/'.join(('resources', 'drivers.default.yml'))) as fp:
            default_logger.info(', '.join(v for v in yaml.load(fp)['drivers'].keys()))

        default_logger.info('\nenvironment variables\n'.upper())
        default_logger.info('\n'.join('%-20s\t%s' % (k, os.environ.get(k, colored('(unset)', 'yellow'))) for k in
                                      __jina_env__))


class NetworkChecker:
    """Check if a Pod is running or not """

    def __init__(self, args: 'argparse.Namespace'):
        from ..peapods.pea import send_ctrl_message
        from ..proto import jina_pb2, add_version
        import time
        ctrl_addr = 'tcp://%s:%d' % (args.host, args.port)
        msg = jina_pb2.Message()
        add_version(msg.envelope)
        msg.request.control.command = jina_pb2.Request.ControlRequest.STATUS
        for j in range(args.retries):
            r = send_ctrl_message(ctrl_addr, msg, timeout=args.timeout)
            if not r:
                print('%s is not responding, retry (%d/%d) in 1s' % (ctrl_addr, j + 1, args.retries))
            else:
                print('%s returns %s' % (ctrl_addr, r))
                exit(0)
            time.sleep(1)
        exit(1)
