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
