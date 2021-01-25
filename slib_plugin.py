from sapprun import SAppRun as SApp

def load_ipython_extension(ip):
    slib_plugin = SApp(ip)
    ip.register_magics(slib_plugin)
