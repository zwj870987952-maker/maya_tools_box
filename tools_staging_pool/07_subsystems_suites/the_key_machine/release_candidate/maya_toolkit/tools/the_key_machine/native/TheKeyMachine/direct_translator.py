"""In-memory Chinese switch; no source replacement or installer."""
from maya_toolkit.tools.the_key_machine.session import guarded_open as open,owned_timer,tracked_widget,literal_module
def apply_chinese_patch():
    from maya_toolkit.tools.the_key_machine import session
    session.language='zh_CN'
    if session.toolbar_module and session.toolbar_module.tb:return session.reload_ui()
    return {'language':'zh_CN'}
def direct_translate():return apply_chinese_patch()
