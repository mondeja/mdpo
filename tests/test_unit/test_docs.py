import os


def test_devref_index():
    devref_index_path = os.path.join('docs', 'devref', 'index.rst')
    with open(devref_index_path, encoding='utf-8') as f:
        devref_index_content = f.read()

    utils_index, implementations_index = [], []
    for line in devref_index_content.splitlines():
        if line.startswith('   mdpo'):
            if line.endswith('.index'):
                implementations_index.append(
                    os.path.join('src', *(line.lstrip().split('/')[:-1])),
                )
            else:
                utils_index.append(line.lstrip(' ').replace('/src', ''))

    src_mdpo_dirpath = os.path.join('src', 'mdpo')
    utils_modules, implementation_packages = [], []
    for filename in os.listdir(src_mdpo_dirpath):
        if filename.startswith('__'):  # ignore __init__.py
            continue

        filepath = os.path.join(src_mdpo_dirpath, filename)
        if os.path.isfile(filepath):
            utils_modules.append(f'mdpo/mdpo.{os.path.splitext(filename)[0]}')
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
