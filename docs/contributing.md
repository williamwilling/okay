# Contributor Guide

The Okay library is used by several teams and any change you make affects all of those teams. The following guidelines help to make sure that you don't accidentally break other people's code, and that they don't accidentally break yours.

## Branches

* Don't commit directly to `master`. `master` should always contain the latest stable release.
* Don't commit directly to `develop`. `develop` contains the latest fixes and features that have already been approved.
* Branch from `develop` before you write or change code. You should use the prefix `feature/` if you're working on a feature and the prefix `fix/` if you're working on a bug fix.
* Don't merge directly to `develop`; create a pull request instead.

## Commits

* Prefer smaller commits over larger commits. If you need more than one line to describe your commit, you should probably split it into multiple commits.
* Don't commit multiple features or bug fixes at once.
* Don't commit files that are specific to your development environment. Feel free to add them to [.gitignore](../.gitignore).

## Unit tests

* Running `pytest` from the project root should always run all unit tests.
* Running all tests should always take less than a second.
* All code has to be covered by unit tests.
* Don't submit a bug fix unless you have a unit test that fails without the fix.
* Don't submit a feature unless you have a unit test that fails without the feature.
* Use the same coding style and naming conventions as the existing tests do.

## Releases

Anytime you merge to `master`, you effectively create a new release. Before you do so, follow these steps.

1. Merge all branches you wish to include in the release into `develop`.
2. Run all unit tests and make sure they all pass.
3. Make sure all new features and feature changes have been documented in both the [user guide](user-guide.md) and the [reference manual](reference.md).
4. Update the [changelog](changelog.md).
5. Update the version number in [setup.py](../setup.py), using [semantic versioning](https://semver.org/).
6. Install the package from `develop` locally to see if it works properly.
7. Merge `develop` into `master`.
8. Create an [annotated tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging#_annotated_tags) with the version number preceeded by a _v_, e.g. `v2.1.5`.
9. [Move the branch](https://stackoverflow.com/a/5471197) with the current major version – e.g. `v2` – to the most recent commit on `master`, or create the branch if it doesn't exist.
10. If you increased the major version for this release, update the [installation instructions](user-guide.md#installation).

Here are some things to keep in mind when creating a release.

* Any breaking change means you need to increase the major part of the version number, no matter how small the change.
* Try to make a release meaningful and don't just create a new release because of that one feature you just added and would like to use. If you really need it, you can branch `master` and merge in the changes you want to create your own pre-release version.