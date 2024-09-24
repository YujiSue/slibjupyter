from slibrun import SLibCodeRun as Runner
def load_ipython_extension(ip):
    plugin = Runner(ip)
    ip.register_magics(plugin)
