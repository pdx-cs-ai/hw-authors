import os, re, sys
from collections import defaultdict

# Regexes for processing.
name = re.compile("[a-z] +([A-Z][a-zA-Z]+)")
punct = re.compile("[^-' a-zA-Z]+")
dash = re.compile("--")
possess = re.compile("'s")

# novel should be an iterable text object.  Returns the
# processed text of novel as a string.
def process(novel):
    # List of paragraphs. Each paragraph is a list of string
    # lines, not newline-terminated.
    pars = list()

    # Accumulate paragraphs, filtering out extraneous lines.
    par = list()
    for line in novel:
        words = line.split()
        if not words or words[0] in {
                "CHAPTER",
                "VOL.",
                "VOLUME",
                "Letter",
                "Chapter",
        }:
            if par and len(par) > 1:
                pars.append(par)
            par = list()
            continue
        par.append(line)
    if par and len(par) > 1:
        pars.append(par)

    # Accumulate names by count of occurrences.
    pnames = defaultdict(int)
    for p in pars:
        text = ' '.join(p)
        for g in name.finditer(text):
            pnames[g.group(1)] += 1

    # Construct the set of names.
    propnames = {n for n in pnames if pnames[n] >= 2}
    propnames -= {
        "Sir",
        "Miss",
        "Mr",
        "Mrs",
        "Madam",
        "Madame",
        "Lord",
        "Lady",
    }

    # Substitute names.
    def clean_names(line):
        line = dash.sub(" ", line)
        line = punct.sub(" ", line)
        cleaned = line.split()
        for i in range(len(cleaned)):
            w = cleaned[i]
            if w in propnames:
                cleaned[i] = "—"
            elif possess.sub("", w) in propnames:
                cleaned[i] = "—'s"
        return " ".join(cleaned) + "\n"

    # Build up the paragraphs with the names cleaned.
    return "\n".join([
        ''.join([
            clean_names(l) for l in p
        ])
        for p in pars
    ])

# Process all available novels.
for fn in os.listdir("hacked/"):
    with open(f"hacked/{fn}", "r") as f_in:
        text = process(f_in)
        with open(fn, "w") as f_out:
            f_out.write(text)
