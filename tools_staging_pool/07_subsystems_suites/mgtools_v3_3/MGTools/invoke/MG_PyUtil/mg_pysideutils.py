def isPySideAvailable():
    try:
        import imp

        _ = imp.find_module("PySide")
        return True
    except:
        return False


def isPySide2Available():
    try:
        import imp

        _ = imp.find_module("PySide2")
        return True
    except:
        return False

