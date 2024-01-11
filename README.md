# RamRalph

A RAM data backend plugin for Ralph (ralph-malph).
Primarily for demonstration purposes.


## Installation via docker compose and make

To bootstrap a test environment on your machine, clone this project, navigate to the
project root and run the `bootstrap` Makefile target:

```bash
$ make bootstrap
```

## Using RamRalph

Once installed, the `ralph` cli is available via the `bin/ralph` script.
Below are some example commands using the `ram` data backend plugin:

```bash
# Read all records from default target collection
$ ./bin/ralph read -b ram

# Read all records from "activities" collection
$ ./bin/ralph read -b ram -t activities

# Find records with ID=1 from default target collection
$ ./bin/ralph read -b ram 1
```
