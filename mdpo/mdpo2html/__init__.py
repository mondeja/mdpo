"""HTML-produced-from-Markdown files translator using PO files as reference."""

import html
import re
import warnings
from collections import OrderedDict
from html.parser import HTMLParser

import md4c
import polib

from mdpo.command import (
    normalize_mdpo_command_aliases,
    parse_mdpo_html_command,
)
from mdpo.io import save_file_checking_file_changed, to_file_content_if_is_file
from mdpo.md import solve_link_reference_targets
from mdpo.po import (
    paths_or_globs_to_unique_pofiles,
    pofiles_to_unique_translations_dicts,
)


PROCESS_REPLACER_TAGS = [
    'p', 'li', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'td', 'th',
]
ALIGNMENT_CHARS = ['\n', ' ', '\t', '\r']


def _html_attrs_to_str(attrs):
    """Converts a dictionary of HTML attributes to its HTML representation.

    Args:
        attrs (dict): Attributes with values

    Returns:
        str: HTML attributes string ready to be used inside a HTML tag.
    """
    response = ''
    for name, value in attrs.items():
        response += name
        if value is not None:
            response += f'="{value}"'
        response += ' '
    return response.rstrip(' ')


class MdPo2HTML(HTMLParser):
    def __init__(
        self,
        pofiles,
        ignore=[],
        merge_adjacent_markups=False,
        code_tags=['code'],
        bold_tags=['b', 'strong'],
        italic_tags=['em', 'i'],
        link_tags=['a'],
        image_tags=['img'],
        ignore_grouper_tags=['div', 'hr'],
        po_encoding=None,
        command_aliases={},
        _check_saved_files_changed=None,
    ):
        self.pofiles = paths_or_globs_to_unique_pofiles(
            pofiles,
            ignore,
            po_encoding=po_encoding,
        )
        self.output = ''
        self.replacer = []
        self._raw_replacement = ''
        self.context = []
        self.current_msgctxt = None

        self.translations = None
        self.translations_with_msgctxt = None

        self.disable = False
        self.disable_next_block = False
        self.enable_next_block = False
        self.disabled_entries = []

        # custom mdpo command resolution
        self.command_aliases = normalize_mdpo_command_aliases(command_aliases)

        # lazy translators mode
        self.merge_adjacent_markups = merge_adjacent_markups

        # pre-commit mode
        self._saved_files_changed = (
            False if _check_saved_files_changed is not None else None
        )

        # references of msgids and their msgstrs changing referenced link
        # targets by their real target, needed to support link references
        # (this variable is redefined when the first link tag `a` is found)
        self.real_link_reference_targets = None

        # code markup
        self.code_tags = code_tags

        # bold markup
        self.bold_tags = bold_tags

        # italic markup
        self.italic_tags = italic_tags

        # link markup
        self.link_tags = link_tags

        # image markup
        self.image_tags = image_tags

        self.ignore_grouper_tags = ignore_grouper_tags

        self.markup_tags = []
        self.markup_tags.extend(self.code_tags)
        self.markup_tags.extend(self.bold_tags)
        self.markup_tags.extend(self.italic_tags)

        self.html_renderer = md4c.HTMLRenderer(md4c.MD_FLAG_TABLES)

        super().__init__()

    def _merge_adyacent_tags(self, html, template_tags):
        for tags_group in [self.bold_tags, self.italic_tags]:
            regexes = []
            for tag in tags_group:
                if tag not in template_tags:
                    continue
                for _tag in tags_group:
                    if _tag not in template_tags:
                        continue
                    regex = fr'</{tag}>\s*<{_tag}>'
                    if regex not in regexes:
                        regexes.append(regex)

            for regex in regexes:
                html = re.sub(regex, ' ', html)

        return html

    def _remove_lastline_from_output_if_empty(self):
        split_output = self.output.split('\n')
        if not split_output[-1]:
            self.output = '\n'.join(split_output)[:-1]

    def _process_replacer(self):
        # print('REPLACER:', self.replacer)

        template_tags = []
        raw_html_template, _current_replacement = ('', '')

        _current_link_target = ''

        _last_start_tag = None
        _last_end_tag = None
        _inside_code = False
        while self.replacer:
            handle, handled, attrs = self.replacer.pop(0)
            if handle == 'start':
                template_tags.append(handled)

                attrs_repr = (
                    f' {_html_attrs_to_str(attrs)}' if attrs else ''
                )

                if handled in self.code_tags:
                    _current_replacement += '`'
                    raw_html_template += f'<{handled}{attrs_repr}>'
                elif handled in self.bold_tags:
                    _current_replacement += '**'
                    raw_html_template += f'<{handled}{attrs_repr}>'
                elif handled in self.italic_tags:
                    _current_replacement += '*'
                    raw_html_template += f'<{handled}{attrs_repr}>'
                elif handled in self.link_tags:
                    title, href = attrs.get('title'), attrs['href']
                    _current_link_target += f'({href}'
                    if title:
                        _current_link_target += f' "{title}"'
                    _current_link_target += ')'

                    raw_html_template += f'<{handled}'

                    # attrs_except_href_title = []
                    for attr, value in attrs.items():
                        if attr in ['title', 'href']:
                            raw_html_template += f' {attr}="{{}}"'
                        # else:
                        #     These attributes are not included in output
                        #    attrs_except_href_title.append((attr, value))
                    # if attrs_except_href_title:
                    #     raw_html_template += ' '
                    # raw_html_template += _html_attrs_to_str(
                    #     attrs_except_href_title) + '>'
                    raw_html_template += '>'
                else:
                    raw_html_template += f'<{handled}{attrs_repr}>'
                _last_start_tag = handled
                if _last_start_tag == 'code':
                    _inside_code = True

            elif handle == 'data':
                if not _inside_code:
                    while '  ' in handled:
                        handled = handled.replace('  ', ' ')

                if all((ch in ALIGNMENT_CHARS) for ch in handled):
                    raw_html_template += handled
                    _current_replacement += handled
                else:
                    raw_html_template += '{}'
                    if _current_link_target:
                        _current_replacement += (
                            f'[{handled}]{_current_link_target}'
                        )
                        _current_link_target = ''
                    else:
                        _current_replacement += handled
            elif handle == 'end':
                raw_html_template += f'</{handled}>'
                if handled in self.code_tags:
                    _current_replacement += '`'
                elif handled in self.bold_tags:
                    _current_replacement += '**'
                elif handled in self.italic_tags:
                    _current_replacement += '*'
                _last_end_tag = handled
                if _last_end_tag == 'code':
                    _inside_code = False
            elif handle == 'comment':
                raw_html_template += f'<!--{handled}-->'
            elif handle == 'startend':
                if handled in self.image_tags:
                    alt, src = attrs.get('alt', ''), attrs['src']
                    _current_replacement += f'![{alt}]({src}'
                    title = attrs.get('title')
                    if title:
                        _current_replacement += f' "{title}"'
                    _current_replacement += ')'

                    raw_html_template += '{}'
                else:
                    attrs_repr = (
                        f' {_html_attrs_to_str(attrs)}' if attrs else ''
                    )
                    raw_html_template += f'<{handled}{attrs_repr}/>'

        _current_replacement = html.unescape(_current_replacement)

        if (self.disable and not self.enable_next_block) \
                or self.disable_next_block:
            replacement = _current_replacement

            self.disabled_entries.append(
                polib.POEntry(
                    msgid=replacement,
                    msgstr='',
                    msgctxt=self.current_msgctxt,
                ),
            )
        else:
            if self.current_msgctxt:
                replacement = self.translations_with_msgctxt[
                    self.current_msgctxt
                ].get(_current_replacement)
            else:
                replacement = self.translations.get(_current_replacement)
            if not replacement:
                replacement = _current_replacement

        for tt in template_tags:
            for tags_group in [self.bold_tags, self.italic_tags]:
                if tt in tags_group:
                    for tag in tags_group:
                        if tag not in template_tags:
                            template_tags.append(tag)

        # print('RAW TEMPLATE:', raw_html_template)
        # print('TEMPLATE TAGS:', template_tags)
        # print(f'CURRENT MSGID: \'{_current_replacement}\'')
        # print('MSGSTR:', replacement)

        html_before_first_replacement = raw_html_template.split('{')[0]
        html_after_last_replacement = raw_html_template.split('}')[-1]
        for tags_group in [self.bold_tags, self.italic_tags, self.code_tags]:
            for tag in tags_group:
                html_before_first_replacement = \
                    html_before_first_replacement.split(f'<{tag}>')[0]
                html_after_last_replacement = \
                    html_after_last_replacement.split(f'</{tag}>')[-1]
            html_before_first_replacement = \
                html_before_first_replacement.split('<a href="')[0]

        html_inner = '\n'.join(
            self.html_renderer.parse(replacement).split('\n')[:-1],
        )
        html_inner = '>'.join(html_inner.split('>')[1:])
        html_inner = '<'.join(html_inner.split('<')[:-1])

        html_template = html_before_first_replacement + html_inner + \
            html_after_last_replacement

        if self.merge_adjacent_markups:
            html_template = self._merge_adyacent_tags(
                html_template,
                template_tags,
            )

        self.output += html_template
        self.context = []

        self.disable_next_block = False
        self.enable_next_block = False
        self.current_msgctxt = None

        # print('________________________________________________')

    def handle_starttag(self, tag, attrs):
        # print('START TAG: %s | POS: %d:%d' % (tag, *self.getpos()))

        if tag in self.ignore_grouper_tags:
            self.context.append(tag)
            attrs_repr = (
                f' {_html_attrs_to_str(OrderedDict(attrs))}' if attrs else ''
            )
            self.output += f'<{tag}{attrs_repr}>'
        elif (
            (self.context and self.context[0] in self.ignore_grouper_tags)
            or (tag == 'ul' and not self.context)
            or (tag in {'blockquote', 'table', 'thead', 'tbody', 'tr'})
        ):
            attrs_repr = (
                f' {_html_attrs_to_str(OrderedDict(attrs))}' if attrs else ''
            )
            self.output += f'<{tag}{attrs_repr}>'
        else:
            if tag == 'a' and self.real_link_reference_targets is None:
                # extend translations to populate link reference msgid-msgstrs
                # with real targets
                self.real_link_reference_targets = (
                    solve_link_reference_targets(self.translations)
                )
                self.translations.update(self.real_link_reference_targets)

            self.replacer.append(('start', tag, OrderedDict(attrs)))
            self.context.append(tag)

    def handle_endtag(self, tag):
        # print('END TAG: %s | POS: %d:%d' % (tag, *self.getpos()))

        if tag in self.ignore_grouper_tags:
            self.output += f'</{tag}>'
            if self.context:
                self.context.pop()
        elif self.context and self.context[0] in self.ignore_grouper_tags:
            self.output += f'</{tag}>'
        elif tag in PROCESS_REPLACER_TAGS:
            self.replacer.append(('end', tag, None))
            self._process_replacer()
        elif tag in ['ul', 'blockquote', 'tr', 'table', 'thead', 'tbody']:
            self.output += f'</{tag}>'
        else:
            self.replacer.append(('end', tag, None))
            if self.context:
                self.context.pop()

    def handle_startendtag(self, tag, attrs):
        # print('STARTEND TAG: %s | POS: %d:%d' % (tag, *self.getpos()))

        if not self.replacer:
            self.output += self.get_starttag_text()
        else:
            self.replacer.append(('startend', tag, OrderedDict(attrs)))

    def handle_data(self, data):
        # print(f'     DATA: \'{data}\'')

        if data:
            if (
                not self.replacer
                or (
                    self.context
                    and self.context[0] in self.ignore_grouper_tags
                )
                or not self.context
            ):
                self.output += data
            else:
                if self.context:
                    data = data.replace('\n', ' ')
                self.replacer.append(('data', data, None))

    def handle_comment(self, data):
        # print(f'     COMMENT: \'{data}\'')

        if self.replacer:
            self.replacer.append(('comment', data, None))
        else:
            data_as_comment = f'<!--{data}-->'
            command, comment = parse_mdpo_html_command(
                data_as_comment,
            )
            if command is None:
                self.output += data_as_comment
            else:
                self._remove_lastline_from_output_if_empty()

                try:
                    command = self.command_aliases[command]
                except KeyError:  # not custom command
                    pass

                if command in (
                    'mdpo-disable-next-block',
                    'mdpo-disable-next-line',
                ):
                    self.disable_next_block = True
                elif command == 'mdpo-disable':
                    self.disable = True
                elif command == 'mdpo-enable':
                    self.disable = False
                elif command in (
                    'mdpo-enable-next-block',
                    'mdpo-enable-next-line',
                ):
                    self.enable_next_block = True
                elif command == 'mdpo-context' and comment:
                    self.current_msgctxt = comment
                elif command == 'mdpo-include-codeblock':
                    warnings.warn(
                        'Code blocks translations are not supported'
                        ' by mdpo2html implementation.',
                        SyntaxWarning,
                    )
                else:
                    self.output += data_as_comment

    def translate(self, filepath_or_content, save=None, html_encoding='utf-8'):
        content = to_file_content_if_is_file(
            filepath_or_content,
            encoding=html_encoding,
        )

        self.translations, self.translations_with_msgctxt = (
            pofiles_to_unique_translations_dicts(self.pofiles)
        )

        self.feed(content)

        if save:
            if self._saved_files_changed is False:
                self._saved_files_changed = save_file_checking_file_changed(
                    save,
                    self.output,
                    encoding=html_encoding,
                )
            else:
                with open(save, 'w', encoding=html_encoding) as f:
                    f.write(self.output)

        self.reset()

        return self.output


def markdown_pofile_to_html(
    filepath_or_content,
    pofiles,
    ignore=[],
    save=None,
    po_encoding=None,
    html_encoding='utf-8',
    command_aliases={},
    **kwargs,
):
    r"""HTML-produced-from-Markdown file translator using PO files.

    Produces a translated HTML file given a previous HTML file (created by a
    Markdown-to-HTML processor) and a set of PO files as reference for msgstrs.

    Args:
        filepath_or_content (str): HTML whose content wants to be translated.
        pofiles (str): Glob for set of pofiles used as reference translating
            the strings to another language.
        ignore (list): List of paths to pofiles to ignore, useful if the glob
            patterns in ``pofiles`` parameter does not fit your requirements.
        save (str): If you pass this parameter as a path to one HTML file,
            even if does not exists, will be saved in the path the output of
            the function.
        html_encoding (str): HTML content encoding.
        po_encoding (str): PO files encoding. If you need different encodings
            for each file, you must define it in the "Content-Type" field of
            each PO file metadata, in the form
            ``"Content-Type: text/plain; charset=<ENCODING>\n"``.
        command_aliases (dict): Mapping of aliases to use custom mdpo command
            names in comments. The ``mdpo-`` prefix in command names resolution
            is optional. For example, if you want to use ``<!-- mdpo-on -->``
            instead of ``<!-- mdpo-enable -->``, you can pass the dictionaries
            ``{"mdpo-on": "mdpo-enable"}`` or ``{"mdpo-on": "enable"}`` to this
            parameter.

    .. rubric:: Known limitations:

    * This implementation doesn't include support for
      :ref:`include-codeblock command<include-codeblock-command>`.


    Returns:
        str: HTML output translated version of the given file.
    """
    return MdPo2HTML(
        pofiles,
        ignore=ignore,
        po_encoding=po_encoding,
        command_aliases=command_aliases,
        **kwargs,
    ).translate(
        filepath_or_content,
        save=save,
        html_encoding=html_encoding,
    )
