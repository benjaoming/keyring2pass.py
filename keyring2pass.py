#!/usr/bin/env python3
"""
============
keyring2pass
============

Imports passwords from the current user's Keyring. Tested on Gnome 3 w/
Seahorse.

Script by Benjamin Bach
License: GPLv3 (because yeah!)

Do you want a long and complicated script downloaded from the interwebz of shitz
to read and write all your passwords?

Probably not, hence this script is kept very short and unbloated for your
comfort. We cannot, however, guarantee for the use of third-party libraries,
for instance python3-keyring. However, it's packaged for Debian already. 

::
  # Get the dependencies
  $ apt install python3-keyring python3-docopt

  # Run the script
  python3 keyring2pass.py


Suggested usage:

List all your current password labels with ``keyring2pass.py list``. Then get a
mental map or write down some future organization of your passwords. One of the
strengths of ``pass`` is that it can sort passwords in a hierarchy / tree
structure. You could for instance go for:

email/<email>
website/<site>/<username>
chat/slack/<company>

After you know the hierarchy you want, start the import.

Here's an example of a full command, suggesting "sites/" as a prefix and picking
up from where it left in case it gets interrupted::

  keyring2pass.py import --log=success.log --skiplog=success.log --prefix=sites/

After importing everything, check that it works and then you can delete all your
keys using the Seahorse UI.
"""
import re
import subprocess
import sys
import time

import docopt
import keyring

__version__ = "0.1"

USAGE = """
keyring2pass

Script by Benjamin Bach
License: GPLv3 (because yeah!)

Usage:
  keyring2pass import [--prefix=PREFIX] [--overwrite] [--log=LOG] [--skiplog=SKIPLOG] [--do-not-ask]
  keyring2pass list [--skiplog=SKIPLOG]
  keyring2pass -h | --help
  keyring2pass --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  --prefix=PREFIX       Prefix the imported labels. [default: imported/]
  --do-not-ask          Don't ask about the label, use default prefix
  --overwrite           Overwrites existing labels/paths instead of prompting
  --log=LOG             Logs each imported label to a file
  --skiplog=SKIPLOG     If a label exists in this file, skip it

Examples:
  keyring2pass import   Import the default keyring to password store
  keyring2pass list     List all labels stored in keyring

"""


def convert(collection, prefix="imported/", overwrite=False, ask=True, log=None):
    """
    :param: overwrite: When False, we prompt the user
    """

    # We just search for an empty string, and we will get everything to import
    # from the collection...
    

    print("Now converting...")
    print("")
    print("Passwords to convert: {}".format(len(collection)))
    print("")
    print("")

    if log:
        log = open(log, "a")

    for key in collection:
        label = key.get_label()

        yes = ""
        while yes.lower() not in ["n", "y"]:
            yes = input("Import '{}'? [Y/n] ".format(label))
        if yes.strip().lower() == "n":
            print("Skipped")
            continue
        
        default_path = prefix + label
        path = None if ask else default_path
        valid_path = re.compile(r"\w+[/\w+]*\w+")
        
        while path is None:
            input_path = input("Import path [{}]: ".format(default_path))
            input_path = input_path.strip()
            if not input_path or valid_path.match(input_path):
                path = input_path if input_path else default_path
        
        options = []
        
        if overwrite:
            options.append("-f")
        
        p = subprocess.Popen(
            ['pass', 'insert'] + options + [path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
        )
        
        # This emulates the user typing the password + ENTER
        pwd_input = key.get_secret().decode("utf-8") + "\n"

        # Write the password twice...
        p.stdin.write(pwd_input)
        time.sleep(0.1)
        p.stdin.write(pwd_input)

        stdout, stderr = p.communicate("\n")
        if p.returncode != 0:
            print("Something went wrong...")
            print(stdout)
            print(stderr)
        elif log:
            log.write(label + "\n")


def main(args=None):

    args = sys.argv[1:]
    docopt_kwargs = dict(
        version=str(__version__),
        options_first=False,
        argv=args,
    )
    arguments = docopt.docopt(USAGE, **docopt_kwargs)

    the_keyring = keyring.get_keyring()
    collection = the_keyring.get_preferred_collection()
    collection=list(collection.search_items(""))
    collection=sorted(collection, key=lambda c: c.get_label())

    if arguments['--skiplog']:
        skiplog = open(arguments['--skiplog'], "a+")
        labels = skiplog.read().split("\n")
        skiplog.close()
        collection = filter(lambda c: c.get_label() not in labels, collection)
        collection = list(collection)

    if arguments['import']:
        prefix = arguments['--prefix']
        convert(
            collection,
            prefix=prefix,
            overwrite=arguments['--overwrite'],
            ask=not arguments['--do-not-ask'],
            log=arguments['--log'],
        )
    elif arguments['list']:
        print("Passwords to convert: {}".format(len(collection)))
        print("")
        print("\n".join([c.get_label() for c in collection]))


if __name__ == "__main__":

    try:
        main(args=sys.argv[1:])
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)


