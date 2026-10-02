"""Full native package; Qt is only imported on explicit UI launch."""
def show():
    from .main import show
    return show()
