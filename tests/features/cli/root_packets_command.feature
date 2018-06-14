Feature: A Root ``packets`` command

Scenario: The user calls the ``packets`` command with no arguments
  Given a click runner
  When the user calls ``packets`` with no arguments
  Then the packets command outputs a help string

Scenario: The user calls the ``packets`` command with the short help argument
  Given a click runner
  When the user calls the ``packets`` with ``-h``
  Then the packets command outputs a help string

Scenario: The user calls the ``packets`` command with the long help argument
  Given a click runner
  When the user calls the ``packets`` with ``--help``
  Then the packets command outputs a help string

