"""Markdown related utilities for mdpo."""


LINK_REFERENCE_REGEX = (
    r'^\[([^\]]+)\]:\s+<?([^\s>]+)>?\s*["\'\(]?([^"\'\)]+)?'
)


def parse_link_references(content):
    """Parses link references found in a Markdown content.

    Args:
        content (str): Markdown content to be parsed.

    Returns:
        list: Tuples with 3 values, target, href and title for each link
        reference.
    """
    import re

    link_reference_re = re.compile(LINK_REFERENCE_REGEX)

    response = []
    for line in content.splitlines():
        linestrip = line.strip()
        if linestrip and linestrip.startswith('['):
            match = re.search(link_reference_re, linestrip)
            if match:
                response.append(match.groups())
    return response


def solve_link_reference_targets(translations):
    """Solve link reference targets in markdown blocks.

    Given a dictionary of msgid/msgstr translations, those link references
    targets will be resolved and returned in a new dictionary.

    Args:
        translations (dict): Mapping of msgid-msgstr entries from which
            the resolved translations will be extracted.

    Returns:
        dict: New created messages with solved link reference targets.
    """
    import re

    link_refereced_link_re = re.compile(r'\[([^\]]+)\]\[([^\]\s]+)\]')
    link_reference_re = re.compile(LINK_REFERENCE_REGEX)

    solutions = {}

    # dictionary with defined link references and their targets
    link_references_text_targets = []

    # compound by dictionaries with `original_msgid`, `original_msgstr` and
    # `link_reference_matchs`
    msgid_msgstrs_with_links = []

    # discover link reference definitions
    for msgid, msgstr in translations.items():
        if msgid.startswith('['):  # filter for performance improvement
            msgid_match = re.search(link_reference_re, msgid.lstrip(' '))
            if msgid_match:
                msgstr_match = re.search(link_reference_re, msgstr.lstrip(' '))
                if msgstr_match:
                    link_references_text_targets.append((
                        msgid_match.groups(),
                        msgstr_match.groups(),
                    ))
        msgid_matchs = re.findall(link_refereced_link_re, msgid)
        if msgid_matchs:
            msgstr_matchs = re.findall(link_refereced_link_re, msgstr)
            if msgstr_matchs:
                msgid_msgstrs_with_links.append((
                    msgid, msgstr, msgid_matchs, msgstr_matchs,
                ))

    # original msgid, original msgstr,
    # msgid link reference matchs, msgstr link reference matchs
    for (
            orig_msgid, orig_msgstr, msgid_linkr_groups, msgstr_linkr_groups,
    ) in msgid_msgstrs_with_links:
        # search if msgid and link reference matchs are inside
        # `link_references_text_targets`
        #
        # if so, replace in original messages link referenced targets with
        # real targets and store them in solutions
        new_msgid, new_msgstr = (None, None)

        for msgid_linkr_group in msgid_linkr_groups:
            for link_reference_text_targets in link_references_text_targets:

                if link_reference_text_targets[0][0] == msgid_linkr_group[1]:
                    replacer = (
                        f'[{msgid_linkr_group[0]}][{msgid_linkr_group[1]}]'
                    )
                    replacement = (
                        f'[{msgid_linkr_group[0]}]'
                        f'({link_reference_text_targets[0][1]})'
                    )

                    if new_msgid is None:
                        # first referenced link replacement in msgid
                        new_msgid = orig_msgid.replace(replacer, replacement)
                    else:
                        # consecutive referenced link replacements in msgid
                        new_msgid = new_msgid.replace(replacer, replacement)
                    break

        # the same game as above, but now for msgstrs

        for msgstr_linkr_group in msgstr_linkr_groups:
            for link_reference_text_targets in link_references_text_targets:

                if link_reference_text_targets[1][0] == msgstr_linkr_group[1]:
                    replacer = (
                        f'[{msgstr_linkr_group[0]}][{msgstr_linkr_group[1]}]'
                    )
                    replacement = (
                        f'[{msgstr_linkr_group[0]}]'
                        f'({link_reference_text_targets[1][1]})'
                    )

                    if new_msgstr is None:
                        # first referenced link replacement in msgid
                        new_msgstr = orig_msgstr.replace(replacer, replacement)
                    else:
                        # consecutive referenced link replacements in msgid
                        new_msgstr = new_msgstr.replace(replacer, replacement)
                    break

        # store in solutions
        solutions[new_msgid] = new_msgstr

    return solutions
