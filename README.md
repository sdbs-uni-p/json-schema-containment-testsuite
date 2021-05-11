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
        "id": "1",
        "description": "not-pushing rules: not const with true",
        "schema1": {
            "not": {
                "const": true
            }
        },
        "schema2": {
            "anyOf": [
                {
                    "not": {
                        "type": "boolean"
                    }
                },
                {
                    "const": false
                }
            ]
        },
        "tests": {
            "s1SubsetEqOfs2": true,
            "s2SubsetEqOfs1": true
        }
    }
]
```
In short, each object has the following attributes:
* id: Uniquely identifies a set of tests within the same file.
* description: The test set description.
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

We use Node 14.151 and Python 3.7 in this project.

## Once you've cloned the repository:
Fetch the submodules we need in this repository:
```shell
// Get the submodule
git submodule update --init --recursive

// Update them to the latest master branch
git submodule foreach git pull origin master
```

## Generate new tests by yourself
To regenerate a new version of the test suite as shown in the `tests` folder:

* Delete all the folders under `tests` directory in the main repository;

* Run the following commands to generate the first part of the test suite based on [`JSON Schema Test Suite`](https://github.com/json-schema-org/JSON-Schema-Test-Suite):
```shell
python bin/testsuite_generation.py
```

## Validate JSON Schema in `tests`
```shell
python bin/test_json.py check
``` 
Then you can get the results of the validation in the terminal.

## Cititation
To refer to this test suite in a publication, please use this BibTeX entry.
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
