import os
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
        os.makedirs('./Codes', exist_ok=True)
        os.makedirs('./App', exist_ok=True)

    def exportScript(self, name, libs, cell):
        header = '#include "sobj.h"\n'
        if 'I' in libs:
            header += '#include "sbioinfo.h"\n'
        header += 'using namespace slib;\n'
        header += 'int main(int argc, const char **argv) {\n'
        footer = '\nreturn 0;\n}'
        path = './Codes/'+name+'.cpp'
        with open(path, mode='w') as f:
            f.write(header)
            f.write(cell)
            f.write(footer)

    def exportSrc(self, name, cell):
        path = './Codes/'+name+'.cpp'
        with open(path, mode='w') as f:
            f.write(cell)

    def compile(self, info):
        cmd = 'g++ -std=c++11 -O2'# -I./Codes -I/usr/local/include/slib -L/usr/local/lib -o ./App/' + info["product"]
        cmd += ' -I./Codes -I/usr/local/include/slib'
        if(info['includes']):
            for head in info['includes']:
                cmd += ' -I'+head
        if(info['codes']):
            for code in info['codes']:
                cmd += ' ./Codes/'+code
        if(info['libs']):
            for lib in info['libs']:
                cmd += ' -l'+lib
        cmd += ' -o ./App/' + info["product"]
        if (info["verbose"]):
            print(cmd)
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if (info["verbose"]):
            print(proc.stdout.splitlines())
        
    def runScript(self, name, slibs, cell):
        self.preset()
        self.exportScript(name, slibs, cell)
        libs = ['sobj', 'curl']
        #
        self.compile({'product':name, 'libs':libs, 'codes':['./Codes/'+name+'.cpp'], 'verbose': True})
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
    def sscriptrun(self, line, cell):
        args = line.split()
        name = args[0]
        libs = args[1]
        output = self.runScript(name, libs, cell)
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