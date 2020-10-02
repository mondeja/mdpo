"""HTML produced from Markdown files translator using pofiles as reference."""

import glob
import re
from collections import OrderedDict
from html.parser import HTMLParser

import polib

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
                 code_start_string='`', code_end_string='`',
                 code_escape_strings=['\\\''], code_tags=['code'],
                 bold_start_string='**', bold_end_string='**',
                 bold_escape_strings=['\\*\\*'], bold_tags=['b', 'strong'],
                 italic_start_string='*', italic_end_string='*',
                 italic_escape_strings=['\\*'], italic_tags=['em', 'i'],
                 link_tags=['a'], ignore_grouper_tags=['div', 'hr']):
        self.pofiles = [polib.pofile(pofilepath) for pofilepath in
                        filter_paths(glob.glob(pofiles), ignore_paths=ignore)]
        self.output = ''
        self.replacer = []
        self._raw_replacement = ''
        self.context = []

        # lazy translators mode
        self.merge_adjacent_markups = merge_adjacent_markups

        # code markup
        self.code_start_string = code_start_string
        self.code_end_string = code_end_string
        self.code_escape_strings = code_escape_strings
        self.code_tags = code_tags

        # bold markup
        self.bold_start_string = bold_start_string
        self.bold_end_string = bold_end_string
        self.bold_escape_strings = bold_escape_strings
        self.bold_tags = bold_tags

        # italic markup
        self.italic_start_string = italic_start_string
        self.italic_end_string = italic_end_string
        self.italic_escape_strings = italic_escape_strings
        self.italic_tags = italic_tags

        # link markup
        self.link_tags = link_tags

        self.markups_handler = OrderedDict(sorted(
            {
                'code': {
                    'start_string': self.code_start_string,
                    'end_string': self.code_end_string,
                    'tags': self.code_tags,
                },
                'bold': {
                    'start_string': self.bold_start_string,
                    'end_string': self.bold_end_string,
                    'tags': self.bold_tags,
                },
                'italic': {
                    'start_string': self.italic_start_string,
                    'end_string': self.italic_end_string,
                    'tags': self.italic_tags,
                },
            }.items(),
            key=lambda k: -max([len(k[1]['start_string']),
                                len(k[1]['end_string'])]),
        ))

        self.markup_strings = []
        for mk_data in self.markups_handler.values():
            if mk_data['start_string'] not in self.markup_strings:
                self.markup_strings.append(mk_data['start_string'])
            if mk_data['end_string'] not in self.markup_strings:
                self.markup_strings.append(mk_data['end_string'])

        self.markup_tags = []
        self.markup_tags.extend(self.code_tags)
        self.markup_tags.extend(self.bold_tags)
        self.markup_tags.extend(self.italic_tags)

        self._template_splitter = self._build_template_splitter()
        self._template_splitter_without_separators = \
            self._template_splitter.replace('|', '')
        self.ignore_grouper_tags = ignore_grouper_tags

        super().__init__()

    def _build_template_splitter(self):
        _template_splitter = ''
        for markup in sorted(list(set(self.markup_strings)), reverse=True):
            _template_splitter += '(%s)|' % (
                ''.join([re.escape(ch) for ch in markup]))
        return _template_splitter.strip('|')

    def _merge_adyacent_tags(self, html, template_tags):
        for markup, mk_data in self.markups_handler.items():
            if markup not in ['bold', 'italic']:
                continue

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

    def _ch_maybe_next_are_markup(self, i, buffer, possible_markups):
        # handler for possible multiples characters in markup strings
        if isinstance(possible_markups, str):
            return len(possible_markups) if \
                buffer[i:i+len(possible_markups)] == possible_markups else 0
        else:  # isinstance(possible_markups (list, tuple)):
            response = 0
            for pm in possible_markups:
                if buffer[i:i+len(pm)] == pm:
                    response = len(pm)
                    break
            return response

    def _build_html_template_by_replacement(self,
                                            raw_html_template,
                                            replacement,
                                            template_tags):
        # get open and close tags in raw template
        open_tag = raw_html_template.split('>')[0] + '>'
        close_tag = '<' + raw_html_template.split('<')[-1]

        html_by_repl_schema = open_tag + '%s' + close_tag
        html_by_repl_inner = ''

        if re.search(r'<[^\s]+\s', raw_html_template):
            tag_indexer = {}
        else:
            tag_indexer = None

        def _get_valid_template_tag(_tags, start=False):
            _tag = None
            for tt in template_tags:
                if tt not in _tags:
                    continue

                if not start or tag_indexer is None:
                    _tag = tt
                    break

                if tt not in tag_indexer:
                    tag_indexer[tt] = 1
                else:
                    tag_indexer[tt] += 1

                _tag_regex = r'<(' + tt + r'[^>]*)>'

                _max_attempts, _attempt = (50, 0)
                while _attempt < _max_attempts:
                    try:
                        _tag = re.search(
                            _tag_regex, raw_html_template
                        ).group(tag_indexer[tt] - _attempt)
                    except IndexError:
                        _attempt += 1
                    else:
                        break
                break
            return _tag

        # print("--------------------------------------")

        # context and formatter {} added (True or False)
        _context, _markupping_counter = ([['root', False]], 0)
        for i, ch in enumerate(replacement):
            if _markupping_counter:
                _markupping_counter -= 1
                continue

            # not markup character case
            if not self._ch_maybe_next_are_markup(i, replacement,
                                                  self.markup_strings):
                if not _context[-1][1]:
                    html_by_repl_inner += '{}'
                    _context[-1][1] = True
                continue

            # process the handler
            for markup, mk_data in self.markups_handler.items():
                # check if context markup found
                markup_start_len = self._ch_maybe_next_are_markup(
                    i, replacement, mk_data['start_string'])
                if markup_start_len:
                    # context start markup found

                    # already in markup context?
                    if _context[-1][0] == markup:

                        # is the end of the context?
                        if mk_data['start_string'] == mk_data['end_string']:
                            markup_end_len = self._ch_maybe_next_are_markup(
                                i, replacement, mk_data['end_string'])

                            if markup_end_len:
                                html_by_repl_inner += '</%s>' % \
                                    _get_valid_template_tag(mk_data['tags'])
                                _context.pop()
                                _context[-1][1] = False
                                _markupping_counter = markup_end_len - 1
                                break

                    else:
                        # enter context
                        _tag = _get_valid_template_tag(
                            mk_data['tags'], start=True)
                        html_by_repl_inner += '<%s>' % _tag
                        _context.append([markup, False])
                        _markupping_counter = markup_start_len - 1
                    break
                # case when opening and closing markup strings differ
                else:
                    markup_end_len = self._ch_maybe_next_are_markup(
                        i, replacement, mk_data['end_string'])
                    if markup_end_len:
                        if _context[-1][0] == markup:
                            html_by_repl_inner += '</%s>' % \
                                _get_valid_template_tag(mk_data['tags'])
                            _context.pop()
                            _context[-1][1] = False
                            _markupping_counter = markup_end_len - 1
                        break

        # print('--------------------------------------')
        html_by_repl = html_by_repl_schema % html_by_repl_inner

        return html_by_repl

    def _fix_replacement_split_links(self, replacement_split):
        response = []

        _inside_link_text = False
        _inside_link_target = False
        _inside_link_title = False
        _exiting_link_title = False
        _current_link_text = None

        for sp in replacement_split:
            _sp = ''
            for i, ch in enumerate(sp):
                if ch == '[' and sp[i - 1] != '\\' and not _inside_link_text:
                    _inside_link_text = True
                    response.append(_sp)
                    _sp = ''
                    continue
                elif ch == ']' and sp[i - 1] != '\\' and _inside_link_text:
                    _inside_link_text = False
                    _current_link_text = _sp
                    _sp = ''
                    continue
                elif ch == '(' and sp[i - 1] == ']' and sp[i - 2] != "\\":
                    _inside_link_target = True
                    continue
                elif _inside_link_target:
                    if ch == ')' and sp[i - 1] != '\\':
                        response.append(_sp)  # target
                        response.append(_current_link_text)  # text
                        _sp = ''
                        _current_link_text = None
                        _inside_link_target = False
                        continue
                    elif ch == ' ':
                        response.append(_sp)  # target
                        _inside_link_target = False
                        _inside_link_title = True
                        _sp = ''
                        continue
                elif _inside_link_title:
                    if _sp == '' and ch == '"':
                        continue
                    if ch == '"' and sp[i - 1] != '\\':
                        response.append(_sp)  # title
                        response.append(_current_link_text)  # text
                        _sp = ''
                        _exiting_link_title = True
                        _inside_link_title = False
                        continue
                elif _exiting_link_title:
                    _exiting_link_title = False
                    continue
                _sp += ch
            if _sp:
                response.append(_sp)

        return [_sp for _sp in response if _sp != '']

    def _process_replacer(self):
        # print("REPLACER:", self.replacer)

        template_tags = []
        raw_html_template, _current_replacement = ('', '')

        _current_link_target = ''

        _last_start_tag = None
        while self.replacer:
            handle, handled, attrs = self.replacer.pop(0)
            if handle == 'start':
                template_tags.append(handled)

                if handled in self.code_tags:
                    _current_replacement += self.code_start_string
                    raw_html_template += '<%s%s>' % (
                        handled,
                        (' ' + html_attrs_tuple_to_string(attrs)
                         if attrs else '')
                    )
                elif handled in self.bold_tags:
                    _current_replacement += self.bold_start_string
                    raw_html_template += '<%s%s>' % (
                        handled,
                        (' ' + html_attrs_tuple_to_string(attrs)
                         if attrs else '')
                    )
                elif handled in self.italic_tags:
                    _current_replacement += self.italic_start_string
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

            elif handle == 'data':
                if all((ch in ALIGNMENT_CHARS) for ch in handled):
                    raw_html_template += handled
                    if _last_start_tag in self.markup_tags:
                        _current_replacement += handled
                    else:
                        if handled == ' ':
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
                    _current_replacement += self.code_end_string
                elif handled in self.bold_tags:
                    _current_replacement += self.bold_end_string
                elif handled in self.italic_tags:
                    _current_replacement += self.italic_end_string
            elif handle == 'comment':
                raw_html_template += '<!--%s-->' % handled
            elif handle == 'startend':
                raw_html_template += '<%s%s/>' % (
                    handled,
                    (' ' + html_attrs_tuple_to_string(attrs) if attrs else '')
                )

        replacement = self.translations.get(
            _current_replacement, _current_replacement)

        # print("RAW TEMPLATE:", raw_html_template)
        # print("TEMPLATE TAGS:", template_tags)
        # print('CURRENT REPLACEMENT: \'%s\'' % _current_replacement)
        # print('REPLACEMENT:', replacement)

        # only build html template by replacement if replacement found
        if replacement != _current_replacement:
            # only build html template replacement if markup character found
            _markup_ch_found = False
            for ch in replacement:
                if ch in ['(', ')']:
                    continue
                if ch in self._template_splitter_without_separators:
                    _markup_ch_found = True

            if _markup_ch_found:
                html_template = self._build_html_template_by_replacement(
                    raw_html_template, replacement, template_tags)
            else:
                html_template = raw_html_template
        else:
            html_template = raw_html_template

        # print('TEMPLATE SPLITTER:', self._template_splitter)
        # print('HTML TEMPLATE:', html_template)

        replacement_split = self._fix_replacement_split_links(list(filter(
            lambda x: x not in self.markup_strings and x,
            re.split(self._template_splitter, replacement)
        )))

        # print('REPLACEMENT SPLIT:', replacement_split)

        html = html_template.format(*replacement_split)
        # print('PARTIAL OUTPUT: \'%s\'' % html)

        if self.merge_adjacent_markups:
            html = self._merge_adyacent_tags(html, template_tags)
            # print("MERGE ADYACENT TAGS OUTPUT: '%s'" % html)

        self.output += html
        self.context = []

        # print("\n________________________________________________\n")

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
