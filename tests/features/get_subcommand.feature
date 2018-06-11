Feature: The get sub-command

Scenario: The user calls the get subcommand with the short help option
  Given a cli runner
  When the user calls the get subcommand with the short help option
  Then it returns an okay status
  And it outputs the help message

Scenario: The user calls the get subcommand with the long help option
  Given a cli runner
  When the user calls the get subcommand with the long help option
  Then it returns an okay status
  And it outputs the help message

Scenario: The user calls the get subcommand with no options
  Given a cli runner
  When the user calls the get subcommand with no options
  Then the GetPackets object is built with the defaults
  And the GetPackets object is run
