"""I/O mdpo utitlites tests."""

import glob
import html
import os
import tempfile

from mdpo.io import (
    filter_paths,
    to_file_content_if_is_file,
    to_glob_or_content,
)


EMPTY_FILES_DIRNAME = 'empty-files'
EMPTY_FILES_GLOBSTR = os.path.join('test', EMPTY_FILES_DIRNAME, '**', '**.md')
EMPTY_FILES_GLOB = glob.glob(EMPTY_FILES_GLOBSTR)

MD_CONTENT_EXAMPLE = "# Hello\n\nI'm markdown\n"


class TestFilterPaths:
    def empty_file_path(self, directory, filename=None):
        args = () if not filename else (filename,)
        return os.path.join('test', EMPTY_FILES_DIRNAME, directory, *args)

    def test_ignore_files_by_filename(self):
        filepaths = filter_paths(
            EMPTY_FILES_GLOB,
            ignore_paths=['foo04.md', 'bar02.md'],
        )
        assert filepaths == [
            self.empty_file_path('bar', 'bar01.md'),
            self.empty_file_path('bar', 'bar03.md'),
            self.empty_file_path('foo', 'foo01.md'),
            self.empty_file_path('foo', 'foo02.md'),
            self.empty_file_path('foo', 'foo03.md'),
        ]

    def test_ignore_directory_by_dirname(self):
        filepaths = filter_paths(EMPTY_FILES_GLOB, ignore_paths=['foo'])

        assert filepaths == [
            self.empty_file_path('bar', 'bar01.md'),
            self.empty_file_path('bar', 'bar02.md'),
            self.empty_file_path('bar', 'bar03.md'),
        ]

    def test_ignore_files_by_filepath(self):
        filepaths = filter_paths(
            EMPTY_FILES_GLOB,
            ignore_paths=[
                self.empty_file_path('foo', 'foo04.md'),
                self.empty_file_path('bar', 'bar02.md'),
            ],
        )

        assert filepaths == [
            self.empty_file_path('bar', 'bar01.md'),
            self.empty_file_path('bar', 'bar03.md'),
            self.empty_file_path('foo', 'foo01.md'),
            self.empty_file_path('foo', 'foo02.md'),
            self.empty_file_path('foo', 'foo03.md'),
        ]

    def test_ignore_files_by_dirpath(self):
        filepaths = filter_paths(
            EMPTY_FILES_GLOB,
            ignore_paths=[self.empty_file_path('foo')],
        )

        assert filepaths == [
            self.empty_file_path('bar', 'bar01.md'),
            self.empty_file_path('bar', 'bar02.md'),
            self.empty_file_path('bar', 'bar03.md'),
        ]


class TestToGlobOrContent:
    def test_glob(self):
        is_glob, parsed = to_glob_or_content(EMPTY_FILES_GLOBSTR)
        assert is_glob
        assert parsed == EMPTY_FILES_GLOB

    def test_content(self):
        is_glob, parsed = to_glob_or_content(MD_CONTENT_EXAMPLE)
        assert not is_glob
        assert parsed == MD_CONTENT_EXAMPLE

    def test_bad_glob_characters_range(self):
        content = html.escape('[s-m]')
        is_glob, parsed = to_glob_or_content(content)
        assert not is_glob
        assert parsed == content


class TestToFileContentIfIsFile:
    def test_file(self):
        with tempfile.NamedTemporaryFile('w+') as tmpfile:
            tmpfile.write(MD_CONTENT_EXAMPLE)
            tmpfile.seek(0)
            md_content = to_file_content_if_is_file(tmpfile.name)
        assert md_content == MD_CONTENT_EXAMPLE

    def test_content(self):
        md_content = to_file_content_if_is_file(MD_CONTENT_EXAMPLE)
        assert md_content == MD_CONTENT_EXAMPLE
