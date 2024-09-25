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
            if '_SFUNC_' in row:
                code = code + 'struct {\n'
                part = row[row.find('_SFUNC_')+7:]
                ret = re.search(r'\s+[a-zA-Z0-9_]+\s+', part)
                code = code + ret.group() + 'operator()'
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
                code = code + row + '\n'
        return code
        
    def makeScriptBody(self):
        body = ''
        scripts = glob.glob("./Scripts/*.cpscrpt")
        sorted(scripts, key=lambda f: os.stat(f).st_mtime, reverse=True)
        for scrpt in scripts:
            with open(scrpt) as f:
                body += f"{f.read()}\n"
        return body
    
    def exportScript(self, name, libs, cell):
        code = self.convertFunc(cell)
        if name[0] == '+':
            name = name[1:]
            path = './Scripts/'+name+'.cpscrpt'
            with open(path, mode='w') as s:
                s.write(code)
            body = self.makeScriptBody()
        else:
            body = self.makeScriptBody() + code		
        
        header = '#include "sobj.h"\n'
        if 'A' in libs:
            header += '#include "sapp.h"\n'
        if 'I' in libs:
            header += '#include "sbioinfo.h"\n'
        header += 'using namespace slib;\n'
        header += 'int main(int argc, const char **argv) {\n'
        footer = '\nreturn 0;\n}'
        path = './Codes/'+name+'.cpp'
        with open(path, 'w') as f:
            f.write(header)
            f.write(body)
            f.write(footer)

    def exportSrc(self, name, cell):
        path = f"./Codes/{name}.cpp"
        with open(path, 'w') as f:
            f.write(cell)

    def compile(self, info):
        cmd = 'g++ -std=c++11 -O2'
        cmd += ' -I./Codes -I/usr/local/include/slib'
        if 'includes' in info:
            for head in info['includes']:
                cmd += ' -I'+head
        if 'codes' in info:
            for code in info['codes']:
                cmd += ' ./Codes/'+code
        if 'libs' in info:
            for lib in info['libs']:
                cmd += ' -l'+lib
        cmd += f" -o ./App/{info['product']}"
        if info['verbose']:
            print(cmd)
            proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
            while proc.poll() is None:
                line = proc.stdout.readline().strip()
                if line:
                    print(line)
        else:
            os.system(cmd)

    def runScript(self, name, slibs, verbose, cell):
        self.preset()
        self.exportScript(name, slibs, cell)
        libs = ['sobj', 'curl']
        if 'A' in slibs:
            libs.append('sapp')
        if 'I' in slibs:
            libs.append('sbioinfo')
        if name[0] == '+':
            name = name[1:]
        self.compile({'product':name, 'libs':libs, 'codes':[name+'.cpp'], 'verbose': verbose})
        proc = subprocess.Popen('./App/'+name, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
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
    @cell_magic
    def savecode(self, line, cell):
        args = line.split()
        name = args[0]
        self.exportSrc(name, cell)
        
    @cell_magic
    def slibscript(self, line, cell):
        args = line.split()
        name = args[0]
        libs = ''
        verbose = False
        if 1 < len(args):
            for i in range(1,  len(args)):
                if args[i] == 'v':
                    verbose = True
                else :
                    libs += args[i]
        output = self.runScript(name, libs, verbose, cell)
        return output
    
    @cell_magic
    def slibcode(self, line, cell):
        args = line.split()
        name = args[0]
        codes = args[1]
        headers = args[2]
        libs = args[3]
        output = self.runCodes(name, codes, headers, libs, cell)
        return output
    
    @cell_magic
    def sappexec(self, line, cell):
        args = line.split()
        name = args[0]
        codes = args[1]
        headers = args[2]
        libs = args[3]
        output = self.runCodes(name, codes, headers, libs, cell)
        return output
