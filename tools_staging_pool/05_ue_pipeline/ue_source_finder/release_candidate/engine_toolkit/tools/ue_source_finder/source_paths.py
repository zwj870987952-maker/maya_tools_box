def read_source_paths(asset):
    """All available import paths with provenance; no has_editor_property assumption."""
    row = {'asset': str(asset.get_path_name()), 'name': str(asset.get_name()), 'paths': [], 'method': None, 'errors': []}
    try:
        data = asset.get_editor_property('asset_import_data')
    except Exception as error:
        row['status'] = 'no_import_data'; row['errors'].append(str(error)); return row
    if data is None:
        row['status'] = 'no_import_data'; return row
    for method in ('get_all_filenames', 'extract_filenames', 'get_first_filename'):
        if not callable(getattr(data, method, None)):
            continue
        try:
            value = getattr(data, method)()
            paths = [value] if method == 'get_first_filename' else list(value or [])
            paths = list(dict.fromkeys(str(p) for p in paths if p))
            if paths:
                row.update(paths=paths, method=method, status='resolved'); return row
        except Exception as error:
            row['errors'].append(method + ': ' + str(error))
    try:
        info = data.get_source_data() if callable(getattr(data, 'get_source_data', None)) else data.get_editor_property('source_data')
        paths = list(dict.fromkeys(str(f.relative_filename) for f in info.source_files if f.relative_filename))
        row.update(paths=paths, method='source_data_raw', status='raw_relative' if paths else 'unresolved')
    except Exception as error:
        row['errors'].append('source_data: ' + str(error)); row['status'] = 'unresolved'
    return row
