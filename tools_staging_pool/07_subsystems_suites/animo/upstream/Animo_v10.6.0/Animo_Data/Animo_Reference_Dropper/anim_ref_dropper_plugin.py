import os
import re
import glob
import hashlib
import shutil
import platform
import subprocess
import urllib.parse
import maya.cmds as cmds
import maya.OpenMayaUI as omui

ANIMATED_EXTENSIONS = {".avi", ".mp4", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".gif"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".tga", ".bmp", ".exr", ".webp", ".psd", ".dpx", ".hdr"}
FRAME_RATE = 24
IMAGE_EXT = "jpg"
MAX_STEM_LENGTH = 24
FFMPEG_ENV_VAR = "ANIMO_FFMPEG_PATH"

MAC_FFMPEG_CANDIDATES = [
    "/opt/homebrew/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/usr/local/opt/ffmpeg/bin/ffmpeg",
    "/opt/local/bin/ffmpeg",
]

LINUX_FFMPEG_CANDIDATES = [
    "/usr/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/snap/bin/ffmpeg",
]

WINDOWS_FFMPEG_CANDIDATES = [
    os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ffmpeg", "bin", "ffmpeg.exe"),
    os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "ffmpeg", "bin", "ffmpeg.exe"),
    os.path.join(os.environ.get("ChocolateyInstall", "C:\\ProgramData\\chocolatey"), "bin", "ffmpeg.exe"),
]

FFMPEG_INSTALL_INSTRUCTIONS = {
    "Darwin": "Install it with Homebrew: open Terminal and run 'brew install ffmpeg', then reopen Maya.",
    "Linux": "Install it with your package manager, e.g. 'sudo apt install ffmpeg' (Debian/Ubuntu), "
             "'sudo dnf install ffmpeg' (Fedora), or 'sudo snap install ffmpeg', then reopen Maya.",
    "Windows": "Download a build from https://www.gyan.dev/ffmpeg/builds/, unzip it, and either add its 'bin' "
               "folder to your PATH or set the ANIMO_FFMPEG_PATH environment variable to the full path of ffmpeg.exe.",
}


class FFmpegNotFoundError(IOError):
    pass


def get_plugin_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
        return os.path.join(script_dir, "Animo_Data", "Animo_Reference_Dropper")


def ffmpeg_executable_name():
    return "ffmpeg.exe" if os.name == "nt" else "ffmpeg"


def is_valid_ffmpeg(candidate_path):
    return bool(candidate_path) and os.path.isfile(candidate_path) and os.access(candidate_path, os.X_OK)


def bundled_ffmpeg_relative_path():
    system = platform.system()
    if system == "Windows":
        return "ffmpeg.exe"
    elif system == "Darwin":
        return os.path.join("mac", "ffmpeg")
    else:
        return os.path.join("linux", "ffmpeg")


def find_bundled_ffmpeg():
    plugin_dir = get_plugin_dir()
    candidate = os.path.join(plugin_dir, bundled_ffmpeg_relative_path())
    if os.path.isfile(candidate) and os.name != "nt" and not os.access(candidate, os.X_OK):
        try:
            os.chmod(candidate, 0o755)
        except OSError:
            pass
    if os.path.isfile(candidate) and platform.system() == "Darwin":
        try:
            subprocess.run(
                ["xattr", "-d", "com.apple.quarantine", candidate],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
    return candidate if is_valid_ffmpeg(candidate) else None


def find_env_override_ffmpeg():
    candidate = os.environ.get(FFMPEG_ENV_VAR)
    return candidate if is_valid_ffmpeg(candidate) else None


def find_ffmpeg_on_path():
    candidate = shutil.which(ffmpeg_executable_name())
    return candidate if is_valid_ffmpeg(candidate) else None


def find_ffmpeg_via_login_shell():
    if os.name == "nt":
        return None

    shell = os.environ.get("SHELL", "/bin/zsh")
    try:
        result = subprocess.run(
            [shell, "-l", "-c", "command -v ffmpeg"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
    except Exception:
        return None

    candidate = result.stdout.decode("utf-8", "ignore").strip()
    return candidate if is_valid_ffmpeg(candidate) else None


def find_ffmpeg_in_known_locations():
    system = platform.system()
    if system == "Darwin":
        candidates = MAC_FFMPEG_CANDIDATES
    elif system == "Linux":
        candidates = LINUX_FFMPEG_CANDIDATES
    else:
        candidates = WINDOWS_FFMPEG_CANDIDATES

    for candidate in candidates:
        if is_valid_ffmpeg(candidate):
            return candidate

    return None


def locate_ffmpeg():
    finders = [
        find_bundled_ffmpeg,
        find_env_override_ffmpeg,
        find_ffmpeg_on_path,
        find_ffmpeg_via_login_shell,
        find_ffmpeg_in_known_locations,
    ]

    for finder in finders:
        found = finder()
        if found:
            return found

    plugin_dir = get_plugin_dir()
    bundled_path = os.path.join(plugin_dir, bundled_ffmpeg_relative_path())
    system = platform.system()
    instructions = FFMPEG_INSTALL_INSTRUCTIONS.get(system, "Install ffmpeg and ensure it is on your PATH.")
    raise FFmpegNotFoundError(
        "ffmpeg not found. Checked bundled path '%s', the %s environment variable, "
        "your PATH, your login shell, and common install locations for %s.\n%s"
        % (bundled_path, FFMPEG_ENV_VAR, system, instructions)
    )


def find_animated_extension(filename):
    lower_name = filename.lower()
    for ext in ANIMATED_EXTENSIONS:
        if ext in lower_name:
            return ext
    return None


def find_image_extension(filename):
    lower_name = filename.lower()
    for ext in IMAGE_EXTENSIONS:
        if ext in lower_name:
            return ext
    return None


def sanitize_name(raw_name):
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", raw_name)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = "video"
    return cleaned


def extract_clean_stem(video_path):
    filename = os.path.basename(video_path)
    ext = find_animated_extension(filename)
    if ext:
        idx = filename.lower().find(ext)
        stem = filename[:idx]
    else:
        stem = os.path.splitext(filename)[0]

    stem = sanitize_name(stem)[:MAX_STEM_LENGTH].strip("_")
    if not stem:
        stem = "video"

    digest = hashlib.md5(video_path.encode("utf-8", "ignore")).hexdigest()[:8]
    return stem + "_" + digest


def make_ref_folder(video_path):
    base_dir = os.path.dirname(video_path)
    name = extract_clean_stem(video_path)
    ref_folder = os.path.join(base_dir, name + "_ref")

    if os.path.isdir(ref_folder) and os.listdir(ref_folder):
        suffix = hashlib.md5(os.urandom(16)).hexdigest()[:6]
        name = name + "_" + suffix
        ref_folder = os.path.join(base_dir, name + "_ref")

    os.makedirs(ref_folder, exist_ok=True)
    return ref_folder, name


def make_startupinfo():
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo


def get_video_duration_seconds(ffmpeg_path, video_path):
    command = [ffmpeg_path, "-i", video_path]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        startupinfo=make_startupinfo()
    )
    output = result.stdout.decode("utf-8", "ignore")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_progress_line(line):
    line = line.strip()
    if "=" not in line:
        return None, None
    key, _, value = line.partition("=")
    return key.strip(), value.strip()


def run_ffmpeg_with_progress(command, name, total_frames):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        startupinfo=make_startupinfo(),
        universal_newlines=True,
        bufsize=1
    )

    max_value = total_frames if total_frames and total_frames > 0 else 100
    cmds.progressWindow(
        title="Animo Reference Dropper",
        status="Converting %s..." % name,
        progress=0,
        minValue=0,
        maxValue=max_value,
        isInterruptable=True
    )

    cancelled = False
    try:
        for raw_line in process.stdout:
            if cmds.progressWindow(query=True, isCancelled=True):
                cancelled = True
                process.terminate()
                break

            key, value = parse_progress_line(raw_line)
            if key is None:
                continue

            if key == "frame":
                try:
                    frame_num = int(value)
                except ValueError:
                    frame_num = 0

                if total_frames and total_frames > 0:
                    shown = min(frame_num, total_frames)
                    cmds.progressWindow(
                        edit=True,
                        progress=shown,
                        status="Converting %s (%d/%d)" % (name, shown, total_frames)
                    )
                else:
                    shown = min(frame_num, max_value)
                    cmds.progressWindow(
                        edit=True,
                        progress=shown,
                        status="Converting %s (frame %d)" % (name, frame_num)
                    )
            elif key == "progress" and value == "end":
                if total_frames and total_frames > 0:
                    cmds.progressWindow(edit=True, progress=total_frames)
                break
    finally:
        process.stdout.close()
        process.wait()
        cmds.progressWindow(endProgress=True)

    return process, cancelled


def convert_to_image_sequence(video_path, frame_rate):
    ffmpeg_path = locate_ffmpeg()
    ref_folder, name = make_ref_folder(video_path)
    output_pattern = os.path.join(ref_folder, name + ".%04d." + IMAGE_EXT)

    duration = get_video_duration_seconds(ffmpeg_path, video_path)
    total_frames = int(duration * frame_rate) if duration else 0

    command = [
        ffmpeg_path,
        "-y",
        "-i", video_path,
        "-r", str(frame_rate),
        "-q:v", "2",
        "-progress", "pipe:1",
        "-nostats",
        output_pattern
    ]

    process, cancelled = run_ffmpeg_with_progress(command, name, total_frames)

    if cancelled:
        raise RuntimeError("Conversion cancelled by user for " + name)

    if process.returncode not in (0, None):
        raise RuntimeError("ffmpeg failed with exit code %s for %s" % (str(process.returncode), name))

    frames = sorted(glob.glob(os.path.join(ref_folder, name + ".*." + IMAGE_EXT)))
    return ref_folder, name, frames


FRAME_NUMBER_RE = re.compile(r"^(.+?)(\d+)(\.[A-Za-z0-9]+)$")


def scan_image_sequence_groups(folder_path):
    groups = {}
    for entry in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, entry)
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(entry)[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            continue

        match = FRAME_NUMBER_RE.match(entry)
        if not match:
            continue

        prefix, digits, matched_ext = match.groups()
        key = (prefix, matched_ext.lower(), len(digits))
        groups.setdefault(key, []).append((int(digits), full_path))

    return groups


def build_sequence_image_plane_from_group(folder_path, group_key, frames):
    prefix, ext, pad_width = group_key
    frames_sorted = sorted(frames, key=lambda item: item[0])
    frame_numbers = [item[0] for item in frames_sorted]
    first_frame_path = frames_sorted[0][1]
    padded_pattern = os.path.join(folder_path, prefix + ("#" * pad_width) + ext)

    plane = cmds.imagePlane(fileName=first_frame_path)
    plane_shape = plane[1]

    cmds.setAttr(plane_shape + ".imageName", padded_pattern, type="string")
    cmds.setAttr(plane_shape + ".useFrameExtension", True)
    cmds.setAttr(plane_shape + ".frameOffset", 0)
    cmds.setAttr(plane_shape + ".frameIn", frame_numbers[0])
    cmds.setAttr(plane_shape + ".frameOut", frame_numbers[-1])
    cmds.setAttr(plane_shape + ".frameCache", len(frame_numbers))

    return plane


def import_image_sequence_folder(folder_path):
    groups = scan_image_sequence_groups(folder_path)
    sequence_groups = {key: value for key, value in groups.items() if len(value) > 1}
    single_frames = [value[0][1] for value in groups.values() if len(value) == 1]

    if not sequence_groups and not single_frames:
        raise RuntimeError("No recognizable image files found in " + folder_path)

    created_planes = []
    for group_key, frames in sequence_groups.items():
        plane = build_sequence_image_plane_from_group(folder_path, group_key, frames)
        created_planes.append(plane)
        display_name = sanitize_name(group_key[0]) or os.path.basename(folder_path)
        cmds.inViewMessage(
            amg="Imported <hl>%s</hl> sequence (%d frames)" % (display_name, len(frames)),
            pos="midCenter",
            fade=True
        )

    for image_path in single_frames:
        plane = import_image_as_reference(image_path)
        created_planes.append(plane)

    return created_planes


def build_image_plane(ref_folder, name, frames):
    if not frames:
        return None

    first_frame = frames[0]
    padded_pattern = os.path.join(ref_folder, name + ".####." + IMAGE_EXT)

    plane = cmds.imagePlane(fileName=first_frame)
    plane_shape = plane[1]

    cmds.setAttr(plane_shape + ".imageName", padded_pattern, type="string")
    cmds.setAttr(plane_shape + ".useFrameExtension", True)
    cmds.setAttr(plane_shape + ".frameOffset", 0)
    cmds.setAttr(plane_shape + ".frameIn", 1)
    cmds.setAttr(plane_shape + ".frameOut", len(frames))
    cmds.setAttr(plane_shape + ".frameCache", len(frames))

    return plane


def build_static_image_plane(image_path):
    plane = cmds.imagePlane(fileName=image_path)
    plane_shape = plane[1]

    cmds.setAttr(plane_shape + ".useFrameExtension", False)

    return plane


def import_image_as_reference(image_path):
    name = sanitize_name(os.path.splitext(os.path.basename(image_path))[0])
    plane = build_static_image_plane(image_path)
    cmds.inViewMessage(amg="Imported <hl>%s</hl> as image plane" % name, pos="midCenter", fade=True)
    return plane


def import_video_as_reference(video_path, frame_rate):
    ref_folder, name, frames = convert_to_image_sequence(video_path, frame_rate)
    plane = build_image_plane(ref_folder, name, frames)
    cmds.inViewMessage(amg="Imported <hl>%s</hl> as image plane" % name, pos="midCenter", fade=True)
    return plane


def video_path_from_url(url):
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)

    if os.name == "nt" and re.match(r"^/[A-Za-z]:", path):
        path = path[1:]

    return os.path.normpath(path)


def prompt_frame_rate():
    try:
        result = cmds.promptDialog(
            title="Frame Rate",
            message="Convert video at this frame rate (fps):",
            text=str(FRAME_RATE),
            button=["OK", "Cancel"],
            defaultButton="OK",
            cancelButton="Cancel",
            dismissString="Cancel"
        )
    except Exception as error:
        cmds.warning(str(error))
        return FRAME_RATE

    if result != "OK":
        return None

    try:
        value = cmds.promptDialog(query=True, text=True)
        frame_rate = int(value)
    except Exception:
        frame_rate = FRAME_RATE

    if frame_rate <= 0:
        frame_rate = FRAME_RATE

    return frame_rate


class AnimRefDropper(omui.MExternalDropCallback):
    instance = None

    def __init__(self):
        omui.MExternalDropCallback.__init__(self)

    def externalDropCallback(self, doDrop, controlName, data):
        if not data.hasUrls():
            return omui.MExternalDropCallback.kMayaDefault

        video_paths = []
        image_paths = []
        folder_paths = []
        try:
            for url in data.urls():
                path = video_path_from_url(url)

                if os.path.isdir(path):
                    folder_paths.append(path)
                    continue

                filename = os.path.basename(path)
                if find_animated_extension(filename):
                    video_paths.append(path)
                elif find_image_extension(filename):
                    image_paths.append(path)
        except Exception as error:
            cmds.warning(str(error))
            return omui.MExternalDropCallback.kMayaDefault

        if not video_paths and not image_paths and not folder_paths:
            return omui.MExternalDropCallback.kMayaDefault

        if not doDrop:
            return omui.MExternalDropCallback.kNoMayaDefaultAndAccept

        if video_paths:
            frame_rate = prompt_frame_rate()
            if frame_rate is None:
                return omui.MExternalDropCallback.kNoMayaDefaultAndAccept
        else:
            frame_rate = FRAME_RATE

        try:
            if cmds.play(query=True, state=True):
                cmds.play(state=False)
        except Exception as error:
            cmds.warning(str(error))

        cmds.waitCursor(state=True)
        created_planes = []
        try:
            ffmpeg_missing = False
            for path in video_paths:
                if ffmpeg_missing:
                    break
                try:
                    plane = import_video_as_reference(path, frame_rate)
                    if plane:
                        created_planes.append(plane)
                except FFmpegNotFoundError as error:
                    ffmpeg_missing = True
                    cmds.confirmDialog(
                        title="ffmpeg Not Found",
                        message=str(error),
                        button=["OK"],
                        defaultButton="OK"
                    )
                except Exception as error:
                    cmds.warning(str(error))

            for path in image_paths:
                try:
                    plane = import_image_as_reference(path)
                    if plane:
                        created_planes.append(plane)
                except Exception as error:
                    cmds.warning(str(error))

            for path in folder_paths:
                try:
                    planes = import_image_sequence_folder(path)
                    if planes:
                        created_planes.extend(planes)
                except Exception as error:
                    cmds.warning(str(error))
        finally:
            cmds.waitCursor(state=False)

        if created_planes:
            transforms = [plane[0] for plane in created_planes]
            try:
                cmds.select(transforms, replace=True)
            except Exception as error:
                cmds.warning(str(error))

        return omui.MExternalDropCallback.kNoMayaDefaultAndAccept


def initializePlugin(plugin):
    AnimRefDropper.instance = AnimRefDropper()
    omui.MExternalDropCallback.addCallback(AnimRefDropper.instance)


def uninitializePlugin(plugin):
    if AnimRefDropper.instance is not None:
        omui.MExternalDropCallback.removeCallback(AnimRefDropper.instance)
        AnimRefDropper.instance = None