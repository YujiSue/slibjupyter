import os
import glob
import re
import subprocess
from IPython.core.magic import Magics, cell_magic, magics_class

@magics_class
class SLibCodeRun(Magics):
    def __init__(self, shell):
        super(SLibCodeRun, self).__init__(shell)
        self.preset()

    @staticmethod
    def preset():
        os.environ['PATH'] += ':/usr/local/bin'
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
            if '_DEF_' in row:
                code += 'struct {\n'
                part = row[row.find('_DEF_')+5:]
                ret = re.search(r'\s+[a-zA-Z0-9_]+\s+', part)
                code += ret.group() + 'operator()'
                fname = re.search(r'\s+[a-zA-Z0-9_]+\s*\(', part)
                code += f'{part[fname.end()-1:]}\n'
                name = part[fname.start():fname.end()-1]
                brackets = brackets + part.count('{') - part.count('}')
                if brackets == 0:
                    code += f'}}{name};'
                else:
                    isFunc = True
            elif isFunc:
                code += f'{row}\n'
                brackets = brackets + row.count('{') - row.count('}')
                if brackets == 0:
                    code += f'}}{name};'
                    isFunc = False
            else:
                code += f'{row}\n'
        return code

    def makeCode(self, name, headers, parts, code):
        hpart = '#include "sobj.h"\n'
        body = 'int main(int argc, const char **argv) {\n'
        #
        for header in headers:
            hpart += f'#include {header}\n'
        hpart += 'using namespace slib;\n'
        hpart += 'using namespace slib::sio;\n'
        hpart += 'using namespace slib::sutil;\n'
        hpart += 'using namespace slib::smath;\n'
        #
        sorted(parts, key=lambda f: os.stat(f).st_mtime, reverse=True)
        for script in parts:
            if script.endswith(f"{name}.cpart"):
                continue
            with open(script) as fp:
                body += f"{fp.read()}\n"
        #
        body += f"{code}\nreturn 0;\n}}"
        #
        path = os.path.join('Codes', f"{name}.cpp")
        with open(path, 'w') as f:
            f.write(hpart)
            f.write(body)

    def compile(self, info):
        # GCC
        cmd = 'g++ -std=c++11 -O2 -I./Codes'
        # 
        cmd += ' -I/usr/local/include/slib'
        # 
        if 'includes' in info:
            for head in info['includes']:
                cmd += f' -I{head}'
        if 'codes' in info:
            for code in info['codes']:
                cmd += f' {code}'
        if 'libs' in info:
            for lib in info['libs']:
                cmd += f' -{lib}'
        cmd += f" -o ./App/{info['product']}"
        if info['verbose']:
            print('*' * 30, ' Compile log ', '*' * 30, '\n >', cmd, '\n')
            proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
            while proc.poll() is None:
                line = proc.stdout.readline().strip()
                if line:
                    print(line)
            print('*' * 75, '\n')
        else:
            os.system(cmd)

    def runScript(self, name, includes, headers, libs, parts, code, verbose):
        self.savecscript(name, code)
        self.makeCode(name, headers, parts, code)
        self.compile({'product':name, 'includes':includes, 'libs':libs, 'codes':[os.path.join('Codes', f"{name}.cpp")], 'verbose': verbose})
        proc = subprocess.Popen(os.path.join('App', name), shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
        while proc.poll() is None:
            while True: 
                line = proc.stdout.readline()
                if line:
                    print(line, end='')
                else:
                    break
        while True: 
            line = proc.stdout.readline()
            if line:
                print(line, end='')
            else:
                break

    def runCodes(self, name, codes, headers, libs, cell):
        self.preset()
        self.exportSrc(name, cell)
        self.compile({'product':name,'includes':headers,'libs':libs,'codes':codes})
        proc = subprocess.Popen('./App/'+name, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
        while proc.poll() is None:
            line = proc.stdout.readline().strip()
            if line:
                print(line)
    
    def savecscript(self, name, code):
        codepath = os.path.join(os.getcwd(), "Scripts", f"{name}.cpart")
        with open(codepath, 'w') as f:
            f.write(code)
        
    @cell_magic
    def slibscript(self, line, cell):
        args = line.split()
        name = args[0]
        libs = ['lsobj', 'lpthread', 'ldl', 'lcurl']
        includes = []
        headers = []
        parts = []
        verbose = False
        code = self.convertFunc(cell)
        for arg in args[1:]:
            if arg[0] == '+':
                parts.append(os.path.join("Scripts", f'{arg[1:]}.cpart'))
            elif ':' in arg:
                if arg.startswith('l:'):
                    libs.append(arg.replace(':', ''))
                elif arg.startswith('h:'):
                    headers.append(f'"{arg[2:]}.h"')
                elif arg.startswith('H:'):
                    includes.append(f'{arg[2:]}')
            else:
                for opt in arg:
                    if opt == 'v':
                        verbose = True
        output = self.runScript(name, includes, headers, libs, parts, code, verbose)
        return output    
    
    @cell_magic
    def slibcode(self, line, cell):
        args = line.split()
        name = args[0]
        codes = args[1]
        headers = args[2]
        libs = args[3]
        output = self.runCode(name, codes, headers, libs, cell)
        return output
    
    @cell_magic
    def slibapp(self, line, cell):
        return ''
