from transify_common import load_transify_module


def run(ui):
    try:
        paste_core = load_transify_module("action_paste_core")
        if paste_core:
            paste_core.run(ui, paste_in_place=False)
    except Exception:
        pass
    finally:
        ui.clear_focus()
