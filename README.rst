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
structure. You could for instance go for::

  email/<email>
  website/<site>/<username>
  chat/slack/<company>

After you know the hierarchy you want, start the import.

Here's an example of a full command, suggesting "sites/" as a prefix and picking
up from where it left in case it gets interrupted::

  keyring2pass.py import --log=success.log --skiplog=success.log --prefix=sites/

After importing everything, check that it works and then you can delete all your
keys using the Seahorse UI.
