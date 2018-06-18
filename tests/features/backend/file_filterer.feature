Feature: A packet-file filterer

Scenario: No start or end time is given
  Given arguments with no start or end time
  When the file filterer is built
  And the file-names are retrieved
  Then it has the expected attributes
  And it returns the expected value

Scenario: The user passes in a non-existent source directory
  Given arguments with a non-existent source directory
  When the user builds the bad FileFilterer object
  Then a ConfigurationError is raised

Scenario: The user passes in a non-directory source
  Given arguments with a source that isn't a directory
  When  the user builds the bad FileFilterer object
  Then a ConfigurationError is raised

Scenario: The user passes in a non-string source
  Given arguments with a source that isn't a string
  When the user builds the bad FileFilterer object
  Then a ConfigurationError is raised

