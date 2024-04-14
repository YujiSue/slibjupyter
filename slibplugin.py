from slibrun import SLibCodeRun as SRunner

def load_ipython_extension(ip):
	slib_plugin = SRunner(ip)
	ip.register_magics(slib_plugin)
