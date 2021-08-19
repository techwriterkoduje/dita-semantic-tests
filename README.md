# DITA Semantic tests

## Quick start

This assumes you know how to use `venv` and `poetry`.

1. We recommend using `venv`
2. Install dependencies by running `poetry install`
3. Run each test in poetry: `poetry run python semantic_testing/config.py`, etc.

Semantic testing is where DITA truly shines. But what is semantic testing?

A simple explanation is “using the semantics of DITA to test documentation”.
What is semantics in DITA? It’s about the named tags and their relations to
other tags in the document structure.

In contrast, there’s no semantics in Markdown. Let’s look at the following
sample of Markdown.

````md
# Running the converter

Run the following command:

```sh
./converter.sh “../images” png svg
```

**Result**: The `converter` creates images in the `out` directory.
````

The semantics of this sample is that there is a heading, a code sample, some
text in bold (Result) and some words related to code sprinkled in the text
("converter" and "out"). This does not really convey a lot of semantics.

In DITA, the sample would look like this:

```xml
<task>
    <title>Running the converter</title>
    <taskbody>
        <steps>
            <step>
                <cmd>Run the following command:</cmd>
                <info>
                    <codeblock outputclass="sh">./converter.sh "../images" png svg</codeblock>
                </info>
                <stepresult>
                    The <apiname>converter</apiname> creates images in the
                    <filepath>out</filepath> directory.
                </stepresult>
            </step>
        </steps>
    </taskbody>
</task>
```

This example shows full semantics in DITA:

- We know that the whole thing is a task which semantically means “something to
  do”.
- The title is “Running the converter”. We could specify this further and say
  that “converter” is an API name. We could then establish a convention that the
  first word in a task title is an action verb. As a result, we could for
  example find all topics that contain the word “run” (or its synonyms, in any
  grammatical form) and grab them for tests.
- There is also granular semantics that tell us about each step, user
  instruction, code sample, file path, and more.

All this semantics, or, in other words, all this meaning allows us to test the
document semantically.

## Running code samples in DITA topics

First, let’s get a list of synonyms of the word we’re looking for. In Python, we
can use the `nltk` library:

```py
from nltk.corpus import wordnet

def get_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonym = l.name().replace('_', ' ')
            if synonym not in synonyms:
                synonyms.append(synonym)
    return synonyms
```

The result for the word “run” should be something like:

```py
[
  "run",
  "running",
  "running play",
  "running game",
  "track",
  "scat",
  "scarper",
  "turn tail",
  "lam",
  "run away",
  "hightail it",
  "bunk",
  "head for the hills",
  "take to the woods",
  "escape",
  "fly the coop",
  "break away",
  "go",
  "pass",
  "lead",
  "extend",
  "operate",
  "flow",
  "feed",
  "course",
  "function",
  "work",
  "range",
  "campaign",
  "play",
  "tend",
  "be given",
  "lean",
  "incline",
  "prevail",
  "persist",
  "die hard",
  "endure",
  "execute",
  "carry",
  "guide",
  "draw",
  "black market",
  "bleed",
  "run for",
  "consort",
  "ply",
  "hunt",
  "hunt down",
  "track down",
  "race",
  "move",
  "melt",
  "melt down",
  "ladder",
  "unravel",
  "linear",
  "operative",
  "functional",
  "working",
]
```

We can use `glob` and `minidom` to find out which tasks match our criteria.

```py
path = './resources/dita/\*_/_.dita'

for file in glob.iglob(path, recursive=True):
    doc = minidom.parse(file)
    if doc.documentElement.tagName == 'task':
        title = doc.getElementsByTagName('title')[0].firstChild.nodeValue
        first_word = title.split()[0]
        if first_word.lower() in synonyms:
            print(f'"{title}" is a matching task, testing')
        else:
            print(f'We will not process {title}')
```

The tests could go like this:

1. In the task, find each step that contains a codeblock.
2. Run the code in the codeblock.
3. If there is a filepath in the `stepresult`, check if that path was created.

```py
path_to_check = None
filepaths = doc.getElementsByTagName("filepath")
if filepaths:
    path_in_topic = [
        filepath.firstChild.nodeValue
        for filepath in filepaths
        if filepath.getAttribute("outputclass") == "output_path"
    ][0]

    path_to_check = app_folder / path_in_topic

    if path_to_check and path_to_check.exists():
        shutil.rmtree(path_to_check)

    command_to_run = doc.getElementsByTagName("codeblock")[0].firstChild.nodeValue

    os.chdir(app_folder)
    stream = os.popen(command_to_run)
    output = stream.readlines()
    result = stream.close()
    if result:
        print(f"Problem running command {command_to_run}: {result}")
    else:
        check_command_output(output, command_to_run)

    if not path_to_check.exists():
        print(f"Specified output path does not exist: {path_to_check}")
    else:
        print(f"Path OK: {path_to_check}")
```

The full test is in the `semantic_testing/running.py` file.

## Check if a file exists

The file `resources/dita/reference.dita` lists some files like this:

```xml
<dlentry>
    <dt>
        <filepath>config.json</filepath>
    </dt>
</dlentry>
```

The simplest semantic test could be:

> For each <filepath>, verify if the file exists.

The code is in `semantic_testing/config.py`, inside the `check_filepath()`
function.

## Parameters listed in configuration files

We can continue parsing `resources/dita/reference.dita` to check if each listed
config file actually contains the properties we claim that it does:

```xml
<dlentry>
    <parml>
        <plentry>
            <pt>quality</pt>
            <pd>Level of image quality to preserve during conversion.</pd>
        </plentry>
    </parml>
</dlentry>
```

Our semantic test goes like this:

> For each `<pt>`, verify if it exists in the file from `<filepath>`.

You can find it in `semantic_testing/config.py`, in the `check_param_list()`
function.

## Spellcheck

In Markdown, running a spellcheck is quite simple. The only rules to follow are:

- Ignore letters between `
- Ignore lines between ```

In DITA, you need to ignore content enclosed by tags like:

- codeph
- codeblock
- apiname
- filepath
- option
- etc.

You also need to specify rules like:

- Except when they have a particular attribute,
- Except in certain XML contexts,
- etc.

This makes spellchecking DITA a little tricky. But you can see our example in
`semantic_testing\spellcheck.py`. Notice the list of excluded elements and
ignored words.
