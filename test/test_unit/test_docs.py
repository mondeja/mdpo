import os


def test_devref_index():
    devref_index_path = os.path.join('docs', 'devref', 'index.rst')
    with open(devref_index_path) as f:
        devref_index_content = f.read()

    utils_index, implementations_index = [], []
    for line in devref_index_content.splitlines():
        if line.startswith('   mdpo'):
            if line.endswith('.index'):
                implementations_index.append(
                    '/'.join(line.lstrip(' ').split('/')[:2]),
                )
            else:
                utils_index.append(line.lstrip(' ').replace('/mdpo', ''))

    utils_modules, implementation_packages = [], []
    for filename in os.listdir('mdpo'):
        if filename.startswith('__'):  # ignore __init__.py
            continue

        filepath = os.path.join('mdpo', filename)
        if os.path.isfile(filepath):
            basename_no_ext = filename.rstrip('.py')
            utils_modules.append(f'mdpo.{basename_no_ext}')
        else:
            implementation_packages.append(filepath)

    # synchronize utilities with devref docs index
    for util_module in utils_modules:
        assert util_module in utils_index
    for util_doc in utils_index:
        assert util_doc in utils_modules

    # synchronize implementations with devref docs index
    for implementation_package in implementation_packages:
        assert implementation_package in implementations_index
    for implementation_doc in implementations_index:
        assert implementation_doc in implementation_packages
