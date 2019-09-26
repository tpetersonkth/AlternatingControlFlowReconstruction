# ACFR
## Overview
ACFR stands for Alternating Control Flow Reconstruction and is a project whose goal is to reconstruct precise control flow of x86 binaries using under and over-approximation alternatingly. The over-approximation is done with the static analysis tool Jakstab and the under-approximation with the dynamic symbolic execution platform manticore.
## Installation

The tool does currently only support debian-based operating systems and has only been tested on Ubuntu 18.04.

### Dependencies: 
* Python 3.6+
* Java
* manticore
* z3
* nasm

Note that the dependencies can be installed automatically executing the installDependencies.sh script.

### Installation instructions
To install the program, cd into the root directory. Then simply execute the setup and compile script:
```
./setup.sh
./compile.sh
```

## Usage
Open two terminals. In one, cd into the SE folder and execute:
```
python manticoreServer.py [port]
```
where [port] is a free port.

Then, use the other terminal to run jakstab. This can be done by executing:
```
jak -m [binary] [options] --dse [port]
```
where [binary] is the binary to analyze, [options] are optional options to pass to jakstab and [port] is the port specified for the manticore server.

## Documentation
TODO

## Questions
Send an email to thpeter@kth.se or create an issue using the issue board.
