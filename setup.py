from distutils.core import setup

setup(
	name='SLibCodeRun',
	version='0.1.0',
	author='Yuji Suehiro',
	author_email='yuji.sue@gmail.com',
	py_modules=['slib_plugin', 'slibrun'],
	url='https://github.com/YujiSue/slibjupyter',
	license='MIT license',
	description='Plugin to run C++ with slib on the Google Colab'
)
