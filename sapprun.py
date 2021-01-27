import os
import subprocess

from IPython.core.magic import Magics, cell_magic, magics_class

@magics_class
class SAppRun(Magics):
    def __init__(self, shell):
        super(SAppRun, self).__init__(shell)
        
    @staticmethod
    def setPath():
        os.environ['PATH'] += ':/usr/local/lib'
        os.environ['LD_LIBRARY_PATH'] += ':/usr/local/lib'
        os.makedirs('./Codes', exist_ok=True)
        os.makedirs('./App', exist_ok=True)

    def exportSrc(self, name, libs, cell):
        header = ''
        if 'O' in libs:
            header += '#include "sobj.h"\n'
        if 'A' in libs:
            header += '#include "sapp.h"\n'
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
            
    def compile(self, name, libs):
        cmd = 'g++ -std=c++11 -I. -I/usr/local/include/slib -L/usr/local/lib -O2 -o ./App/' + name
        cmd += ' ./Codes/' + name + '.cpp'
        if 'O' in libs:
            cmd += ' -lsobj'
        if 'A' in libs:
            cmd += ' -lsapp'
        if 'I' in libs:
            cmd += ' -lsbioinfo'
        cmd += ' -lcurl'
        #print(cmd)
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #print(proc.stdout.splitlines())
        
    def run(self, name, libs, cell):
        self.setPath()
        self.exportSrc(name, libs, cell)
        self.compile(name, libs)
        proc = subprocess.run('./App/'+name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(proc.stdout.splitlines())
        return None

    @cell_magic
    def sapprun(self, line, cell):
        args = line.split()
        name = args[0]
        libs = args[1]
        output = self.run(name, libs, cell)
        return output
