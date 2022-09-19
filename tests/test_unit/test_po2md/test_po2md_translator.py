import os

from mdpo.po2md import Po2Md


def test___slots__(class_slots):
    slots = class_slots(Po2Md)
    assert slots

    po2md_implementation_filepath = os.path.join(
        'src', 'mdpo', 'po2md', '__init__.py',
    )
    with open(po2md_implementation_filepath) as f:
        content = f.read()

    for slot in slots:
        assert content.count(f'self.{slot}') > 1
