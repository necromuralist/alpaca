Feature: Capture Info helper

Scenario: The CaptureInfo is built
  Given The CaptureInfo is built
  When the attributes are checked
  Then they are the expected attributes

Scenario: The first timestamp is grabbed
  Given The CaptureInfo is built
  When the first timestamp is grabbed
  Then it is the correct timestamp

Scenario: The last timestamp is grabbed
  Given The CaptureInfo is built
  When the last timestamp is grabbed
  Then it is the correct timestamp
