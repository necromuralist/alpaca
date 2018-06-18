Feature: A packet retriever

Scenario: The user builds a GetPackets object
 Given valid arguments
 When the user builds the GetPackets object
 Then the Get Packets object has the expected attributes

Scenario: The user calls the GetPackets object
  Given valid arguments
  When the user builds the GetPackets object
  And calls the GetPackets object
  Then the GetPackets object performs the expected steps

Scenario: The user passes in the start time
  Given arguments with the start time
  When the user builds the GetPackets object
  Then the GetPackets object has the correct start time

Scenario: The user passes in an invalid start time
  Given arguments with a bad start time
  When the user builds the bad GetPackets object
  Then a ConfigurationError is raised

Scenario: The user passes in a non-string start time
  Given arguments with a non-string start time
  When the user builds the bad GetPackets object
  Then a ConfigurationError is raised

Scenario: The user passes in the end time
  Given arguments with the end time
  When the user builds the GetPackets object
  Then the GetPackets object has the correct end time

Scenario: The user passes in an invalid end time
  Given arguments with a bad end time
  When the user builds the bad GetPackets object
  Then a ConfigurationError is raised

Scenario: The user passes in a non-string end time
  Given arguments with a non-string end time
  When the user builds the bad GetPackets object
  Then a ConfigurationError is raised

Scenario: The user passes in a glob
  Given arguments with a source glob
  When the user builds the GetPackets object
  Then the GetPackets object has the expected values

Scenario: The user passes in a target directory
  Given arguments with a target
  When the user builds the GetPackets object
  Then the GetPackets object has the expected values
