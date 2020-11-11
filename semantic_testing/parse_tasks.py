import glob
from xml.dom import minidom
from nltk.corpus import wordnet


def get_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonym = l.name().replace('_', ' ')
            if synonym not in synonyms:
                synonyms.append(synonym)
    return synonyms


synonyms = get_synonyms('convert')
path = './resources/dita/**/*.dita'

for file in glob.iglob(path, recursive=True):
    doc = minidom.parse(file)
    if doc.documentElement.tagName == 'task':
        title = doc.getElementsByTagName('title')[0].firstChild.nodeValue
        first_word = title.split()[0]
        if first_word.lower() in synonyms:
            print(f'"{title}" is a matching task, testing')
        else:
            print(f'We will not process {title}')
