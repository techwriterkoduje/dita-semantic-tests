#TODO: Add print messages for successful results
from pathlib import Path
from typing import List
from xml.dom import minidom

from spellchecker import SpellChecker

excluded_elements = [
    'codeph',
    'codeblock',
    'apiname',
    'filepath',
    'parmname',
    'pt',
    'cmdname',
    'option'
]

ignored_words = [
    'svg',
    'png',
    'jpg',
]


def get_text_from_child_nodes(element, aggregator: List):
    for child in element.childNodes:
        if child.nodeType == child.TEXT_NODE:
            aggregator.append(child.data)
        elif child.nodeType == child.ELEMENT_NODE and child.tagName not in excluded_elements:
            get_text_from_child_nodes(child, aggregator)


spell = SpellChecker()
working_dir = Path(__file__).absolute()
topics_dir = working_dir.parent.parent / "resources" / "dita"

for topic in topics_dir.rglob('*.dita'):
    doc = minidom.parse(topic.__str__())
    all_text = []
    get_text_from_child_nodes(doc, all_text)
    all_words = spell.split_words("".join(all_text))
    unknown_words = [word for word in spell.unknown(all_words) if word not in ignored_words]
    if unknown_words:
        for word in unknown_words:
            print(f'Unknown word in {topic.name}: "{word}", did you mean "{spell.correction(word)}"')
    else:
        print(f'Perfect spelling in file {topic.name}')
