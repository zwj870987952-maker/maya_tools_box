"""Preserve original suite and build an isolated, narrowly repaired runtime edition."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import tokenize
import io

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT/'tools_staging_pool/01_animation/anim_polish_premium_v1_23'
RC = UNIT/'release_candidate'
PACKAGE = RC/'maya_toolkit/tools/anim_polish_premium_v1_23'
PREFIX = 'maya_toolkit.tools.anim_polish_premium_v1_23.vendor.animPolish'
HELPERS = 'maya_toolkit.tools.anim_polish_premium_v1_23'


def replace_function(source, name, body):
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    lines = source.splitlines(keepends=True)
    lines[function.lineno:function.end_lineno] = ['\n']+['\t'+line+'\n' for line in body.splitlines()]
    return ''.join(lines)


def namespace_source(text):
    # Only executable import tokens and callback strings change; docstrings remain provenance.
    tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    result = []
    for token in tokens:
        if token.type == tokenize.STRING:
            value = ast.literal_eval(token.string)
            if isinstance(value,str) and 'import animPolish' in value and not token.string.startswith(("'''",'"""')):
                value = value.replace('import animPolish','import importlib; import '+PREFIX)
                value = re.sub(r'\breload\s*\(', 'importlib.reload(', value)
                token = tokenize.TokenInfo(token.type,repr(value),token.start,token.end,token.line)
        result.append(token)
    text = tokenize.untokenize(result)
    text = re.sub(r'(?m)^import animPolish(?=\.|\s|$)','import '+PREFIX,text)
    return text


def main():
    (PACKAGE/'vendor/animPolish').mkdir(parents=True,exist_ok=True)
    (PACKAGE/'vendor/__init__.py').write_text('',encoding='utf-8')
    original = UNIT/'animPolish'
    for source in UNIT.iterdir():
        if source.name=='release_candidate':
            continue
        if source.is_dir():
            shutil.copytree(source,PACKAGE/'upstream'/source.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
        elif source.is_file():
            (PACKAGE/'upstream').mkdir(exist_ok=True)
            shutil.copyfile(source,PACKAGE/'upstream'/source.name)
    functions, settings, patches = {}, [], []
    for p in sorted(original.glob('*.py')):
        raw = p.read_text(encoding='utf-8-sig')
        tree = ast.parse(raw)
        for node in tree.body:
            if not isinstance(node,ast.FunctionDef):
                continue
            defaults = [None]*(len(node.args.args)-len(node.args.defaults))+list(node.args.defaults)
            params = []
            for param, default in zip(node.args.args,defaults):
                params.append(dict(name=param.arg,required=default is None,
                                   **({} if default is None else {'default':ast.literal_eval(default)})))
            key = p.stem+'.'+node.name
            functions[key] = dict(module=p.stem,name=node.name,parameters=params,line=node.lineno,end_line=node.end_lineno,
                                  callable_by_api=not p.stem.startswith('user_') and key!='ui.saveSettings_run')
            if key=='ui.saveSettings':
                for call in ast.walk(node):
                    if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='saveSettings_run':
                        settings.append([ast.literal_eval(a) for a in call.args[:3]])
        transformed = namespace_source(raw)
        # Accept native JSON lists as well as the legacy UI's literal list strings.
        transformed = re.sub(r'(\w+) = ast\.literal_eval \(\1\)',r'\1 = ast.literal_eval(\1) if isinstance(\1, str) else list(\1)',transformed)
        if p.stem in ('growShrink','iron'):
            line = '\tdfrmverts = ast.literal_eval(dfrmverts) if isinstance(dfrmverts, str) else list(dfrmverts)\n'
            assert transformed.count(line)==2
            transformed = transformed.replace(line,line+"\tif not dfrmverts:\n\t\tdfrmverts = cmds.ls('{}.vtx[*]'.format(geo), fl=True)\n",1)
        if p.stem=='ui':
            transformed = transformed.replace('import imp\n','')
            transformed = transformed.replace("user_data_directory = ''",'from '+HELPERS+' import state as _state\nuser_data_directory = _state.data_directory().as_posix()')
            transformed = replace_function(transformed,'saveSettings','return _state.save_settings()')
            transformed = replace_function(transformed,'loadSettings','return _state.load_settings()')
            transformed = replace_function(transformed,'defaultSettings','return _state.default_settings()')
            transformed = transformed.replace('exec ("val = cmds.{} (\'{}\', q = 1, {} = 1)".format (typ,name,flag))','val = getattr(cmds,typ)(name,q=True,**{flag:True})')
            needle = '\t\t\t\t\tcaching.exp_geos (path, geos)\n\t\t\t\tcache_refreshList ()'
            assert transformed.count(needle)==1
            transformed = transformed.replace(needle,'\t\t\t\tcaching.exp_geos (path, geos)\n\t\t\t\tcache_refreshList ()')
        if p.stem=='copyPasteAttrs':
            transformed = transformed.replace('import sys\n','import sys\nfrom '+HELPERS+' import state as _state\n')
            transformed = replace_function(transformed,'copy','return _state.copy_attrs(path,k)')
            transformed = replace_function(transformed,'paste','return _state.paste_attrs(path)')
        if p.stem=='assignColors':
            transformed = transformed.replace('import sys\n','import sys\nimport ast\n')
            transformed = transformed.replace("exec ('getList = {}'.format (get))",'getList = ast.literal_eval(get)')
        if p.stem=='sculptPose':
            transformed = transformed.replace('import re\n','import re\nfrom '+HELPERS+' import state as _state\n')
            transformed = transformed.replace('def sortCB():','def _sortCB_original():')
            transformed += '\n\ndef sortCB():\n\treturn _state.defer_sort(_sortCB_original)\n'
        if p.stem=='subdue':
            transformed = transformed.replace('import sys\n','import sys\nfrom '+HELPERS+' import state as _state\n')
            needle = "mel.eval ('doCreateGeometryCache 6 { \"2\", \"1\", \"10\", \"OneFile\", \"1\", \"\",\"0\",\"\",\"0\", \"add\", \"0\", \"1\", \"1\",\"0\",\"1\",\"mcx\",\"0\" } ;')"
            assert transformed.count(needle)==1
            transformed = transformed.replace(needle,'_state.create_subdue_cache()')
        if p.stem=='caching':
            transformed = transformed.replace('import ast\n','import ast\nfrom '+HELPERS+'.file_guards import cache_io\n')
            for name, leaf, writing in [('exp_cams','cameras.ma',True),('exp_geos','geometry.abc',True),('imp_cams','cameras.ma',False),('imp_geos','geometry.abc',False),('swap','geometry.abc',False)]:
                transformed = transformed.replace('def '+name+' (',"@cache_io('{}', {})\ndef {} (".format(leaf,writing,name))
            transformed = transformed.replace('path2 = path1.replace (old,version)',"path2 = '{}/geometry.abc'.format(path)")
        transformed = '\n'.join(line.rstrip() for line in transformed.splitlines()).rstrip()+'\n'
        ast.parse(transformed)
        target = PACKAGE/'vendor/animPolish'/p.name
        target.write_text(transformed,encoding='utf-8')
        if raw!=transformed:
            patches.extend(difflib.unified_diff(raw.splitlines(),transformed.splitlines(),fromfile='upstream/animPolish/'+p.name,tofile='vendor/animPolish/'+p.name,lineterm=''))
    resources = {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted((PACKAGE/'upstream').rglob('*')) if p.is_file()}
    catalog = dict(functions=functions,resources=resources,settings_fields=settings,legacy_state_files=['user_settings.py','user_copyPasteAttrs.py'])
    (PACKAGE/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    docs = RC/'docs/tools'
    docs.mkdir(parents=True,exist_ok=True)
    (docs/'anim_polish_runtime_changes.diff').write_text('\n'.join(patches)+'\n',encoding='utf-8')
    rows = ['# AnimPolish 过程签名与覆盖目录','','完整原始 suite 保留；user_* 的 2 个 run 和文件句柄辅助过程由 UI/状态层管理，不作为 JSON invoke。签名行号指向 upstream。','','| 过程 | 参数 | 原行号 | JSON invoke |','| --- | --- | --- | --- |']
    for key, fn in functions.items():
        params = ', '.join(p['name'] if p['required'] else p['name']+'='+repr(p['default']) for p in fn['parameters'])
        rows.append('| `{}` | `{}` | {} | {} |'.format(key,params,fn['line'],'是' if fn['callable_by_api'] else '内部/旧状态脚本'))
    (docs/'anim_polish_premium_v1_23_functions.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    files = sorted(p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    promotion = dict(tool_id='anim_polish_premium_v1_23',registration=dict(module='anim_polish_premium_v1_23',class_name='AnimPolishTool'),
                     files=[dict(source=p.relative_to(RC).as_posix(),target=p.relative_to(RC).as_posix()) for p in files],
                     resources=list(resources),source='../animPolish',dependencies=['Maya MEL/cmds','Interactive Maya for original UI, Channel Box and paint tools','AbcExport/AbcImport loaded explicitly by user for Alembic','existing maya_toolkit core/framework'],
                     license='Copyright Frigging Awesome Studios / Josh Sobel; local bundle has no standalone redistribution license; no relicensing claim',
                     change_summary='Entire original 19-file bundle and 160 signatures retained; private runtime namespace and narrow fixes, JSON settings/clipboard outside code, guarded cache I/O, framework API/UI/provenance and promotion metadata.',
                     verification_limitations=['Real GUI and all rig/topology-dependent workflows pending','Settings/clipboard JSON intentionally replace executable state scripts','Source exception swallowing remains; success return alone cannot prove deformation','Cache file writes/imports cannot be fully reversed with scene Undo','Redistribution permission not established'],acceptance_required=True)
    (RC/'promotion.json').write_text(json.dumps(promotion,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(functions=len(functions),api_functions=sum(x['callable_by_api'] for x in functions.values()),resources=len(resources))))


if __name__=='__main__':
    main()
