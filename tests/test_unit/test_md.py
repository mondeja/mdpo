import os

from mdpo.md import MarkdownSpanWrapper


def test_MarkdownSpanWrapper___slots__(class_slots):
    slots = class_slots(MarkdownSpanWrapper)
    assert slots

    md_util_filepath = os.path.join('src', 'mdpo', 'md.py')
    with open(md_util_filepath, encoding='utf-8') as f:
        content = f.read()

    for slot in slots:
        assert content.count(f'self.{slot}') > 1
