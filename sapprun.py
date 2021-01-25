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
        
    def compile(name, libs):
        cmd = 'g++ -std=c++11 -I. -I/usr/local/include.slib -L/usr/local/lib -O2 -o ./App/' + name
        cmd += ' ./Codes/' + name + '.cpp'
        if 'O' in libs:
            cmd += ' -lsobj'
        if 'A' in libs:
            cmd += ' -lsapp'
        if 'I' in libs:
            cmd += ' -lsbioinfo'
        cmd += ' -lcurl'
        print(cmd)
        
    def run(self, name, libs):
        self.setPath()
        self.compile(name, libs)
        return None

    @cell_magic
    def sapprun(self, line, cell):
        try:
            args = line.split()
            name = args[1]
            print(line.split())
        except SystemExit as e:
            print('err')
            return 
        file_path = './Codes/'
        output = self.run(name, 'O')
        return output
