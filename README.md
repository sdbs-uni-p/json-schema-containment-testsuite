# [json-schema-containment-testsuite](https://github.com/sdbs-uni-p/json-schema-containment-testsuite)

This repository contains a set of JSON schemas that can be used to test JSON Schema containment checkers.

It is meant to be language agnostic and should require only a JSON parser.

The structure of the repository, as well as the general concept, is greatly inspired by the [JSON Schema Test Suite](https://github.com/json-schema-org/JSON-Schema-Test-Suite). 

## Structure of a Test

The tests in this suite are contained in the `tests` directory at the root of
this repository. Inside that directory is a subdirectory for each draft or
version of the specification.

Inside each draft directory, there are a number of `.json` files and one or more
special subdirectories. The subdirectories contain `.json` files meant for a
specific testing purpose, and each `.json` file logically groups a set of test
cases together. Often the grouping is by property under test, but not always.

The subdirectories are described in the next section.

Inside each `.json` file is a single array containing objects. It's easiest to illustrate the structure of these with an example:

```json
[
    {
        "id": 1,
        "schema1": {
            "anyOf": [
                {
                    "enum": [
                        1,
                        2,
                        3
                    ]
                },
                {
                    "not": {
                        "enum": [
                            1,
                            2,
                            3
                        ]
                    }
                }
            ]
        },
        "schema2": true,
        "tests": {
            "s1SubsetEqOfs2": true,
            "s2SubsetEqOfs1": true
        }
    }
]
```
In short, each object has the following attributes:
* id: Uniquely identifies a set of tests within the same file.
* schema1: The first schema for JSON Schema containment checking.
* schema2: The second schema for JSON Schema containment checking.
* tests: The groundtruth of tests.
    - s1SubsetEqOfs2: Whether schema1 is a subset of schema2, or both schemas are equivalent.
    - s2SubsetEqOfs1: Whether schema2 is a subset of schema1, or both schemas are equivalent.


## Test Subdirectories

There is currently only one subdirectory that may exist within each draft
directory. This is:

1. `optional/`: Contains tests that are considered optional.

# Prerequisites
Python 3 is used for test generation.

## Cloning the repository
```shell
// Clone repository with submodules
git clone --recurse-submodules https://github.com/sdbs-uni-p/json-schema-containment-testsuite.git
```

or

```shell
// Clone repository
git clone https://github.com/sdbs-uni-p/json-schema-containment-testsuite.git

// Get the submodules
git submodule update --init --recursive
```
## Generate new tests by yourself
To regenerate a new version of the test suite as shown in the `tests` folder:

* Delete all folders under `tests` directory in the main repository;

* Run the following commands to generate the test suite based on [`JSON Schema Test Suite`](https://github.com/json-schema-org/JSON-Schema-Test-Suite):
```shell
// Update submodules (JSON-Schema-Test-Suite) to latest commit
git submodule foreach git pull origin master

// Generate tests
python bin/testsuite_generation.py
```

## Validate generetaed tests
Validates all tests in the `tests` directory.

```shell
python bin/test_json.py
``` 

## Cititation
There is a demo paper for this test suite, presented at [ER 2021](https://www.er2021.org): [A Test Suite for JSON Schema Containment](http://ceur-ws.org/Vol-2958/paper4.pdf).

To refer to this test suite in a publication, please cite the demo paper above and/or use this BibTex entry:
```BibTeX
@Misc{jsc_test_suite,
  author =  {Lyes Attouche and Mohamed Amine Baazizi and Dario Colazzo and Yunchen Ding and Luca Escher and Michael Fruth and Giorgio Ghelli and Carlo Sartiani and Stefanie Scherzinger},
  title =   {A Test Suite for Checking JSON Schema Containment},
  note =    {\url{https://github.com/sdbs-uni-p/json-schema-containment-testsuite}},
  year =    2021
}
``` 

## Acknowledgments:
This work was partly funded by Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) grant #385808805. 
