.. _Version_History:

===============
Version History
===============

v0.1.1
======

* In ``block.py``, make sure ``get_script_configuration`` returns an empty string if the script configuration is empty.

  The original implementation was returning "{}", which causes issues with the ScriptQueue.
  It will now check if the configuration is empty and return an empty string in this case.

v0.1.0
======

* Initial definition of the classes that allow specifying observing blocks with scheduling constraints.
* Add support to build conda package in TSSW CI system.
