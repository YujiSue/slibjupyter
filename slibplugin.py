from slibrun import SLibCodeRun as SRunner
def load_ipython_extension(ip):
	slibplugin = SRunner(ip)
	ip.register_magics(slibplugin)