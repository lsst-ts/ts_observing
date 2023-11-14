.. _Version_History:

===============
Version History
===============

v0.1.2
======

* Fix an issue when generating script configuration that contain sexagesimal coordinates starting with "+0".
  These coordinates were dumped without quotes around the coordinates which breaks the parsing of the configuration.

v0.1.1
======

* In ``block.py``, make sure ``get_script_configuration`` returns an empty string if the script configuration is empty.

  The original implementation was returning "{}", which causes issues with the ScriptQueue.
  It will now check if the configuration is empty and return an empty string in this case.

v0.1.0
======

* Initial definition of the classes that allow specifying observing blocks with scheduling constraints.
* Add support to build conda package in TSSW CI system.
