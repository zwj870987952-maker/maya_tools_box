# GETOOLS is under the terms of the MIT License
# Copyright (c) 2018-2024 Eugene Gataulin (GenEugene). All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Author: Eugene Gataulin tek942@gmail.com https://www.linkedin.com/in/geneugene https://discord.gg/heMxJhTqCz
# Source code: https://github.com/GenEugene/GETools or https://app.gumroad.com/geneugene
import ast
import os
from pathlib import Path
import maya.cmds as cmds
_basicFileDialogFilter='*.txt';_dialogStyle=2

def ReadLogic(filepath,*args):
    path=Path(filepath)
    if not path.is_file():return None
    if path.stat().st_size>1024*1024:raise ValueError('Preset exceeds 1 MiB')
    result={}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if ' = ' not in line:continue
        key,value=line.strip().split(' = ',1)
        if not key.isidentifier() or key in result:raise ValueError('Invalid or duplicate preset key')
        result[key]=ast.literal_eval(value)
    return result,str(path)

def SaveLogic(filepath,variablesDictionary,title='',*args):
    path=Path(filepath)
    if path.exists():raise FileExistsError('Choose a new preset filename; existing file protected')
    if not isinstance(variablesDictionary,dict) or len(variablesDictionary)>1000:raise ValueError('Invalid preset')
    lines=[str(title).replace('\n',' '),''] if title else []
    for key,value in variablesDictionary.items():
        if not isinstance(key,str) or not key.isidentifier():raise ValueError('Invalid preset key')
        ast.literal_eval(repr(value));lines.append(key+' = '+repr(value))
    text='\n'.join(lines)+'\n'
    if len(text.encode('utf-8'))>1024*1024:raise ValueError('Preset exceeds 1 MiB')
    if not path.parent.is_dir():raise ValueError('Output parent must exist')
    with path.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)
    return str(path)

def SaveDialog(startingDirectory,variablesDict,title='',*args):
    result=cmds.fileDialog2(fileMode=0,startingDirectory=startingDirectory,fileFilter=_basicFileDialogFilter,dialogStyle=2)
    if result: return SaveLogic(result[0],variablesDict,title)
def ReadDialog(startingDirectory,*args):
    result=cmds.fileDialog2(fileMode=1,startingDirectory=startingDirectory,fileFilter=_basicFileDialogFilter,dialogStyle=2)
    return ReadLogic(result[0]) if result else None
