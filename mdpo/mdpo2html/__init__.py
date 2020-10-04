"""HTML produced from Markdown files translator using pofiles as reference."""

import glob
import re
from collections import OrderedDict
from html.parser import HTMLParser

import polib
import md4c

from mdpo.html import (
    get_html_attrs_tuple_attr,
    html_attrs_tuple_to_string,
)
from mdpo.io import (
    filter_paths,
    to_file_content_if_is_file,
)

PROCESS_REPLACER_TAGS = ['p', 'li', 'h1', 'h2', 'h3',
                         'h4', 'h5', 'h6', 'td', 'th']
ALIGNMENT_CHARS = ['\n', ' ', '\t', '\r']


class MdPo2HTML(HTMLParser):
    def __init__(self, pofiles, ignore=[], merge_adjacent_markups=False,
                 code_tags=['code'], bold_tags=['b', 'strong'],
                 italic_tags=['em', 'i'], link_tags=['a'],
                 ignore_grouper_tags=['div', 'hr']):
        self.pofiles = [polib.pofile(pofilepath) for pofilepath in
                        filter_paths(glob.glob(pofiles), ignore_paths=ignore)]
        self.output = ''
        self.replacer = []
        self._raw_replacement = ''
        self.context = []

        # lazy translators mode
        self.merge_adjacent_markups = merge_adjacent_markups

        # code markup
        self.code_tags = code_tags

        # bold markup
        self.bold_tags = bold_tags

        # italic markup
        self.italic_tags = italic_tags

        # link markup
        self.link_tags = link_tags

        self.ignore_grouper_tags = ignore_grouper_tags

        self.markups_handler = OrderedDict(sorted(
            {
                'bold': {
                    'start_string': '**',
                    'end_string': '**',
                    'tags': self.bold_tags,
                },
                'italic': {
                    'start_string': '*',
                    'end_string': '*',
                    'tags': self.italic_tags,
                },
            }.items(),
            key=lambda k: -max([len(k[1]['start_string']),
                                len(k[1]['end_string'])]),
        ))

        self.markup_tags = []
        self.markup_tags.extend(self.code_tags)
        self.markup_tags.extend(self.bold_tags)
        self.markup_tags.extend(self.italic_tags)

        self.html_renderer = md4c.HTMLRenderer(md4c.MD_FLAG_TABLES)

        super().__init__()

    def _build_template_splitter(self):
        _template_splitter = ''
        for markup in sorted(list(set(self.markup_strings)), reverse=True):
            _template_splitter += '(%s)|' % (
                ''.join([re.escape(ch) for ch in markup]))
        return _template_splitter.strip('|')

    def _merge_adyacent_tags(self, html, template_tags):
        for markup, mk_data in self.markups_handler.items():
            regexes = []
            for tag in mk_data['tags']:
                if tag not in template_tags:
                    continue
                for _tag in mk_data['tags']:
                    if _tag not in template_tags:
                        continue
                    regex = r'</%s>\s*<%s>' % (tag, _tag)
                    if regex not in regexes:
                        regexes.append(regex)

            for regex in regexes:
                html = re.sub(regex, ' ', html)
        return html

    def _process_replacer(self):
        # print("REPLACER:", self.replacer)

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

                if handled in self.code_tags:
                    _current_replacement += '`'
                    raw_html_template += '<%s%s>' % (
                        handled,
                        (' ' + html_attrs_tuple_to_string(attrs)
                         if attrs else '')
                    )
                elif handled in self.bold_tags:
                    _current_replacement += '**'
                    raw_html_template += '<%s%s>' % (
                        handled,
                        (' ' + html_attrs_tuple_to_string(attrs)
                         if attrs else '')
                    )
                elif handled in self.italic_tags:
                    _current_replacement += '*'
                    raw_html_template += '<%s%s>' % (
                        handled,
                        (' ' + html_attrs_tuple_to_string(attrs)
                         if attrs else '')
                    )
                elif handled in self.link_tags:
                    title = get_html_attrs_tuple_attr(attrs, "title")
                    _current_link_target += '(%s' % get_html_attrs_tuple_attr(
                        attrs, "href")
                    if title:
                        _current_link_target += ' "%s"' % title
                    _current_link_target += ')'

                    raw_html_template += '<%s' % handled

                    attrs_except_href_title = []
                    for attr, value in attrs:
                        if attr in ['title', 'href']:
                            raw_html_template += ' %s="{}"' % attr
                        else:
                            attrs_except_href_title.append(attr)
                    raw_html_template += html_attrs_tuple_to_string(
                        attrs_except_href_title) + '>'
                else:
                    raw_html_template += '<%s%s>' % (
                        handled,
                        ' ' + html_attrs_tuple_to_string(attrs)
                        if attrs else '')
                _last_start_tag = handled
                if _last_start_tag == 'code':
                    _inside_code = True

            elif handle == 'data':
                if not _inside_code:
                    handled = handled.replace('  ', ' ')

                if all((ch in ALIGNMENT_CHARS) for ch in handled):
                    raw_html_template += handled
                    if _last_start_tag in self.markup_tags:
                        _current_replacement += handled
                    else:
                        _current_replacement += handled
                else:
                    raw_html_template += '{}'
                    if _current_link_target:
                        _current_replacement += '[%s]%s' % (
                            handled, _current_link_target)
                        _current_link_target = ''
                    else:
                        _current_replacement += handled
            elif handle == 'end':
                raw_html_template += '</%s>' % handled
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
                raw_html_template += '<!--%s-->' % handled
            elif handle == 'startend':
                raw_html_template += '<%s%s/>' % (
                    handled,
                    (' ' + html_attrs_tuple_to_string(attrs) if attrs else '')
                )

        replacement = self.translations.get(
            _current_replacement, _current_replacement)

        for tt in template_tags:
            for tags_group in [self.bold_tags, self.italic_tags]:
                if tt in tags_group:
                    for tag in tags_group:
                        if tag not in template_tags:
                            template_tags.append(tag)

        # print("RAW TEMPLATE:", raw_html_template)
        # print("TEMPLATE TAGS:", template_tags)
        # print('CURRENT MSGID: \'%s\'' % _current_replacement)
        # print('MSGSTR:', replacement)

        html_before_first_replacement = raw_html_template.split('{')[0]
        html_after_last_replacement = raw_html_template.split('}')[-1]
        for tags_group in [self.bold_tags, self.italic_tags, self.code_tags]:
            for tag in tags_group:
                html_before_first_replacement = \
                    html_before_first_replacement.split('<%s>' % tag)[0]
                html_after_last_replacement = \
                    html_after_last_replacement.split('</%s>' % tag)[-1]
            html_before_first_replacement = \
                html_before_first_replacement.split('<a href="')[0]

        html_inner = '\n'.join(
            self.html_renderer.parse(replacement).split('\n')[:-1])
        html_inner = '>'.join(html_inner.split('>')[1:])
        html_inner = '<'.join(html_inner.split('<')[:-1])

        html = html_before_first_replacement + html_inner + \
            html_after_last_replacement

        if self.merge_adjacent_markups:
            html = self._merge_adyacent_tags(html, template_tags)

        self.output += html
        self.context = []

    def handle_starttag(self, tag, attrs):
        # print("START TAG: %s | POS: %d:%d" % (tag, *self.getpos()))

        if tag in self.ignore_grouper_tags:
            self.context.append(tag)
            self.output += '<%s%s>' % (
                tag, ' ' + html_attrs_tuple_to_string(attrs) if attrs else '')
        elif self.context and self.context[0] in self.ignore_grouper_tags:
            self.output += '<%s%s>' % (
                tag, ' ' + html_attrs_tuple_to_string(attrs) if attrs else '')
        elif tag == 'ul' and not self.context:
            self.output += '<%s%s>' % (
                tag, ' ' + html_attrs_tuple_to_string(attrs) if attrs else '')
        elif tag in ['blockquote', 'table', 'thead', 'tbody', 'tr']:
            self.output += '<%s%s>' % (
                tag, ' ' + html_attrs_tuple_to_string(attrs) if attrs else '')
        else:
            self.replacer.append(('start', tag, attrs))
            self.context.append(tag)

    def handle_endtag(self, tag):
        # print("END TAG: %s | POS: %d:%d" % (tag, *self.getpos()))

        if tag in self.ignore_grouper_tags:
            self.output += '</%s>' % tag
            if self.context:
                self.context.pop()
        elif self.context and self.context[0] in self.ignore_grouper_tags:
            self.output += '</%s>' % tag
        elif tag in PROCESS_REPLACER_TAGS:
            self.replacer.append(('end', tag, None))
            self._process_replacer()
        elif tag in ['ul', 'blockquote', 'tr', 'table', 'thead', 'tbody']:
            self.output += '</%s>' % tag
        else:
            self.replacer.append(('end', tag, None))
            if self.context:
                self.context.pop()

    def handle_startendtag(self, tag, attrs):
        # print("STARTEND TAG: %s | POS: %d:%d" % (tag, *self.getpos()))

        if not self.replacer:
            self.output += self.get_starttag_text()
        else:
            self.replacer.append(('startend', tag, attrs))

    def handle_data(self, data):
        # print("     DATA: '%s'" % (data))

        if data:
            if not self.replacer or (
                    self.context and
                    self.context[0] in self.ignore_grouper_tags) or \
                    not self.context:
                self.output += data
                return
            else:
                if self.context:
                    data = data.replace('\n', ' ')
                self.replacer.append(('data', data, None))

    def handle_comment(self, data):
        # print("     COMMENT: '%s'" % (data))

        if not self.replacer:
            self.output += '<!--%s-->' % data
        else:
            self.replacer.append(('comment', data, None))

    def translate(self, filepath_or_content, save=None):
        content = to_file_content_if_is_file(filepath_or_content)

        self.translations = {}
        for pofile in self.pofiles:
            for entry in pofile:
                self.translations[entry.msgid] = entry.msgstr

        self.feed(content)

        if save:
            with open(save, "w") as f:
                f.write(self.output)

        self.reset()

        return self.output


def markdown_pofile_to_html(filepath_or_content, pofiles, ignore=[],
                            save=None, **kwargs):
    return MdPo2HTML(
        pofiles, ignore=ignore, **kwargs
    ).translate(filepath_or_content, save=save)
