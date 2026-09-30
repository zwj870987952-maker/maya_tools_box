"""Private sequence, checked FFmpeg execution and explicit output publication."""
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def absolute(value, directory=False):
    if not isinstance(value, str) or not value or '\x00' in value:
        raise ValueError('明确绝对路径需要')
    path = Path(value)
    if not path.is_absolute() or str(path).startswith(('\\\\', '//')):
        raise ValueError('需要本地绝对路径')
    resolved = path.resolve()
    if path.is_symlink() or directory and not resolved.is_dir():
        raise ValueError('路径不可为symlink，目录须已存在')
    return resolved


def executable(value=''):
    found = value or shutil.which('ffmpeg')
    if not found:
        raise ValueError('未找到FFmpeg，使用明确ffmpeg_path或配置PATH')
    path = absolute(found)
    if not path.is_file() or os.name == 'nt' and path.suffix.lower() != '.exe':
        raise ValueError('FFmpeg需要现有可执行文件')
    return str(path)


def signature(path):
    if path.is_symlink() or path.exists() and not path.is_file():
        raise ValueError('输出目标须普通文件，不能是symlink/目录')
    if not path.exists():
        return None
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns]


def destinations(directory, names, overwrite=False, increment=False):
    directory = absolute(directory, directory=True)
    outputs = []
    for base, extensions in names:
        if not isinstance(base, str) or not re.fullmatch(r'[^<>:"/\\|?*\x00-\x1f]{1,120}', base) or base.endswith(('.', ' ')) or base.upper().split('.')[0] in {'CON', 'PRN', 'AUX', 'NUL'} | {'COM' + str(i) for i in range(1, 10)} | {'LPT' + str(i) for i in range(1, 10)}:
            raise ValueError('文件名须有效Windows普通basename，不能包含路径/设备名')
        chosen = base
        if increment:
            i = 1
            chosen = base + '_1'  # Original 增序 always starts at _1.
            while any((directory / (chosen + e)).exists() for e in extensions):
                i += 1
                if i > 10000:
                    raise ValueError('增序候选过多')
                chosen = base + '_' + str(i)
        current = []
        for extension in extensions:
            p = directory / (chosen + extension)
            state = signature(p)
            if state is not None and not overwrite:
                raise ValueError('输出已存在，需明确overwrite或increment: ' + str(p))
            current.append({'path': str(p), 'before': state})
        outputs.append(current)
    flat = [v['path'].casefold() for group in outputs for v in group]
    if len(flat) != len(set(flat)):
        raise ValueError('多个相机输出名冲突')
    return outputs


def publish(staged, target, overwrite=False):
    staged = Path(staged)
    final = Path(target['path'])
    if not staged.is_file() or staged.stat().st_size == 0:
        raise RuntimeError('无有效新输出')
    current = signature(final)
    if current != target['before']:
        raise RuntimeError('输出在预检后改变，拒绝覆盖: ' + str(final))
    if current is not None:
        if not overwrite:
            raise RuntimeError('未授权覆盖')
        os.replace(staged, final)
    else:
        # Atomic no-clobber publication from the same output filesystem.
        os.link(staged, final)
    return str(final)


def invoke(command, timeout=600):
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError('FFmpeg失败 code=' + str(result.returncode) + ': ' + result.stderr[-8000:])
    return result


def sequence_files(folder):
    folder = absolute(folder, directory=True)
    files = []
    for p in folder.iterdir():
        match = re.fullmatch(r'(?:renamed_capture|capture)\.([-+]?\d+)\.jpg', p.name, flags=re.I)
        if match and p.is_file() and not p.is_symlink():
            files.append((int(match.group(1)), p))
    files.sort(key=lambda item: item[0])
    if not files or len(files) > 20000 or len({n for n, _ in files}) != len(files):
        raise ValueError('需要1..20000张唯一编号capture/renamed_capture.JPG')
    return [p for _, p in files]


def prepare_sequence(files, target, hold=1):
    target = Path(target)
    target.mkdir()
    processed = [files[i] for i in range(0, len(files), hold) for _ in range(hold)]
    for i, src in enumerate(processed):
        shutil.copy2(src, target / ('renamed_capture.%04d.jpg' % i))
    return len(processed)


def encode_images(ffmpeg, folder, fps, count, output, audio='', offset=0, timeout=600):
    command = [ffmpeg, '-nostdin', '-y', '-thread_queue_size', '8', '-framerate', str(fps), '-start_number', '0', '-i', str(Path(folder) / 'renamed_capture.%04d.jpg')]
    if audio:
        if offset:
            command.extend(['-itsoffset', str(offset / fps)])
        command.extend(['-i', audio])
    command.extend(['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2'])
    if audio:
        command.extend(['-c:a', 'aac'])
    command.extend(['-frames:v', str(count), str(output)])
    invoke(command, timeout)
    return str(output)


def mp4(ffmpeg, source, output, timeout=600):
    invoke([ffmpeg, '-nostdin', '-y', '-i', str(source), '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', str(output)], timeout)
    return str(output)


def gif(ffmpeg, source, fps, size, output, timeout=600):
    invoke([ffmpeg, '-nostdin', '-y', '-i', str(source), '-vf', 'fps=' + str(fps) + ',scale=' + str(size[0]) + ':' + str(size[1]) + ':flags=lanczos', str(output)], timeout)
    return str(output)


def mux_audio(ffmpeg, source, audio, offset_seconds, duration, output, timeout=600):
    invoke([ffmpeg, '-nostdin', '-y', '-i', str(source), '-itsoffset', str(offset_seconds), '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-t', str(duration), str(output)], timeout)
    return str(output)
