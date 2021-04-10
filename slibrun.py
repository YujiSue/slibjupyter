import os
import glob
import re
import subprocess

from IPython.core.magic import Magics, cell_magic, magics_class

@magics_class
class SLibCodeRun(Magics):
	def __init__(self, shell):
		super(SLibCodeRun, self).__init__(shell)

	@staticmethod
	def preset():
		os.environ['PATH'] += ':/usr/local/lib'
		os.environ['LD_LIBRARY_PATH'] += ':/usr/local/lib'
		os.makedirs('./Scripts', exist_ok=True)
		os.makedirs('./Codes', exist_ok=True)
		os.makedirs('./App', exist_ok=True)

	def convertFunc(self, cell):
		code = ''
		name = ''
		isFunc = False
		brackets = 0
		rows = cell.splitlines()
		for row in rows:
			if ('_SFUNC_' in row):
				code = code + 'struct {\n'
				part = row[row.find('_SFUNC_')+7:]
				ret = re.search(r'\s+[a-zA-Z0-9_]+\s+', part)
				code  = code + ret.group() + 'operator()'
				fname = re.search(r'\s+[a-zA-Z0-9_]+\s*\(', part)
				code = code + part[fname.end()-1:] + '\n'
				name = part[fname.start():fname.end()-1]
				brackets = brackets + part.count('{') - part.count('}')
				if brackets == 0:
					code = code + '}' + name + ';'

				else:
					isFunc = True

			elif isFunc:
				code = code + row + '\n'
				brackets = brackets + row.count('{') - row.count('}')
				if brackets == 0:
					code = code + '}' + name + ';'
					isFunc = False

			else:
				code = code + row

		return code

	def makeScriptBody(self):
		body = ''
		scripts = glob.glob("./Scripts/*.cpscrpt")
		sorted(scripts, key=lambda f: os.stat(f).st_mtime, reverse=True)
		for scrpt in scripts:
			with open(scrpt, mode='r') as f:
				body = body + f.read()
		return body

	def exportScript(self, name, libs, cell):
		code = self.convertFunc(cell)
		path = './Scripts/'+name+'.cpscrpt'
		with open(path, mode='w') as s:
			s.write(code)
		body = self.makeScriptBody()
		header = '#include "sobj.h"\n'
		if ('I' in libs):
			header += '#include "sbioinfo.h"\n'
		header += 'using namespace slib;\n'
		header += 'int main(int argc, const char **argv) {\n'
		footer = '\nreturn 0;\n}'
		path = './Codes/'+name+'.cpp'
		with open(path, mode='w') as f:
			f.write(header)
			f.write(body)
			f.write(footer)

	def exportSrc(self, name, cell):
		path = './Codes/'+name+'.cpp'
		with open(path, mode='w') as f:
			f.write(cell)

	def compile(self, info):
		cmd = 'g++ -std=c++11 -O2'
		cmd += ' -I./Codes -I/usr/local/include/slib'
		if ('includes' in info):
			for head in info['includes']:
				cmd += ' -I'+head
		if ('codes' in info):
			for code in info['codes']:
				cmd += ' ./Codes/'+code
		if ('libs' in info):
			for lib in info['libs']:
				cmd += ' -l'+lib
		cmd += ' -o ./App/' + info["product"]
		if info['verbose']:
			print(cmd)
			proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			res = proc.stdout.splitlines()
			for row in res:
				print(row.decode())
		else:
			os.system(cmd)
		
	def runScript(self, name, slibs, verbose, cell):
		self.preset()
		self.exportScript(name, slibs, cell)
		libs = ['sobj', 'curl']
		if ('I' in slibs):
			libs.append('sbioinfo')
		if ('S' in slibs):
			libs.append('sscience')
		self.compile({'product':name, 'libs':libs, 'codes':[name+'.cpp'], 'verbose': verbose})
		proc = subprocess.run('./App/'+name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		res = proc.stdout.splitlines()
		for row in res:
			print(row.decode())
		return None

	def runCodes(self, name, codes, headers, libs, cell):
		self.preset()
		self.exportSrc(name, cell)
		self.compile({'product':name,'includes':headers,'libs':libs,'codes':codes})
		proc = subprocess.run('./App/'+name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		res = proc.stdout.splitlines()
		for row in res:
			print(row.decode())
		return None

	@cell_magic
	def scompile(self, line, cell):
		args = line.split()

	@cell_magic
	def save_scode(self, line, cell):
		args = line.split()
		name = args[0]
		self.exportSrc(name, cell)

	@cell_magic
	def run_sscript(self, line, cell):
		args = line.split()
		name = args[0]
		libs = ''
		if (1 < len(args)):
			libs = args[1]
		verbose = False
		if (2 < len(args)):
			if args[2] == 'v':
				verbose = True
		output = self.runScript(name, libs, verbose, cell)
		return output
	
	@cell_magic
	def scoderun(self, line, cell):
		args = line.split()
		name = args[0]
		codes = args[1]
		headers = args[2]
		libs = args[3]
		output = self.runCodes(name, codes, headers, libs, cell)
		return output

	@cell_magic
	def sapprun(self, line, cell):
		args = line.split()
		name = args[0]
		codes = args[1]
		headers = args[2]
		libs = args[3]
		output = self.runCodes(name, codes, headers, libs, cell)
		return output