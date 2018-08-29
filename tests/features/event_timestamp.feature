Feature: A WiFi packet event timestamp extractor 

Scenario: A Packet Event Timestamper is created
  Given a set of settings for the event timestamper
  When the timestamper is built
  Then the timestamper has the expected settings

Scenario: The user gives a non-existent log-path
  Given a group of settings with a non-existent log-file
  When the Timestamper is built with the bad settings
  Then a Configuration Error is raised

Scenario: The packets are checked by the user
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are retrieved by the user
  Then scapy.sniff is called

Scenario: The Client sends a probe request to the AP
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the last probe request is retrieved
  Then it has the expected timestamp

Scenario: The AP sends a probe response to the Client
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the probe response is retrieved
  Then it has the expected timestamp

Scenario: The client sends an authentication request to the AP
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the authentication request is retrieved
  Then it has the expected timestamp

Scenario: The AP sends an authentication response to the client
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the authentication response is retrieved
  Then it has the expected timestamp

Scenario: The Client sends an association request to the AP
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the association request is retrieved 
  Then it has the expected timestamp

Scenario: The AP sends an association response to the Client
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the association response is retrieved
  Then it has the expected timestamp

Scenario: The AP starts the four-way handshake
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the start of the handshake is in the packets
  And the authentication nonce is retrieved
  Then it has the expected timestamp
  And the timestamper's step attribute is correct

Scenario: The client responds to the start of the handshake
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the start of the handshake is in the packets
  And the clients response to the start of the handshake is in the packets
  And the authentication snonce is retrieved
  Then it has the expected timestamp
  And the timestamper's step attribute is correct

Scenario: The AP sends the GTK to the client
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the start of the handshake is in the packets
  And the clients response to the start of the handshake is in the packets
  And the AP's response to the snonce is in the packets
  And the group temporal key is retrieved
  Then it has the expected timestamp
  And the timestamper's step attribute is correct

Scenario: The client sends the GTK acknowledgement to the AP
  Given a set of settings for the event timestamper
  When the timestamper is built
  And the packets are set up
  And the start of the handshake is in the packets
  And the clients response to the start of the handshake is in the packets
  And the AP's response to the snonce is in the packets
  And the client's response to the GTK is in the packets
  And the client's acknowledgement is retrieved
  Then it has the expected timestamp
  And the timestamper's step attribute is correct
