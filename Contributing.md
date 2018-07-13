# Contributing guidelines

We welcome any kind of contribution to our software, from simple comment or question to a full fledged 
[pull request](https://help.github.com/articles/about-pull-requests/). 
Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

A contribution can be one of the following cases:

1. you have a question;
1. you think you may have found a bug (including unexpected behavior);
1. you want to make some kind of change to the code base (e.g. to fix a bug, to add a new feature, to update 
documentation).

The sections below outline the steps in each case.

## You have a question

1. use the search functionality [here](https://github.com/EC-Earth/ece2cmor3/issues) to see if someone already filed the 
same issue;
1. if your issue search did not yield any relevant results, make a new issue;
1. apply the "Question" label; apply other labels when relevant.

## You think you may have found a bug

1. use the search functionality [here](https://github.com/EC-Earth/ece2cmor3/issues) to see if someone already filed the 
same issue;
1. if your issue search did not yield any relevant results, make a new issue, making sure to provide enough information 
to the rest of the community to understand the cause and context of the problem. 
Depending on the issue, you may want to include:
    - the [SHA hashcode](https://help.github.com/articles/autolinked-references-and-urls/#commit-shas) of the commit 
    that is causing your problem;
    - information about the nature of the EC-Earth output you are working with and possibly the metadata that you are 
    using; 
    - information about the HPC platform or OS you are using for your job;
1. apply relevant labels to the newly created issue.

## You want to make some kind of change to the code base

1. (**important**) announce your plan to the rest of the community _before you start working_. 
This announcement should be in the form of a (new) issue;
1. (**important**) wait until some kind of consensus is reached about your idea being a good idea;
1. if needed, fork the repository to your own Github profile and create your own feature branch off of the latest 
master commit. While working on your feature branch, make sure to stay up to date with the master branch by pulling in 
changes, possibly from the 'upstream' repository (follow the instructions 
[here](https://help.github.com/articles/configuring-a-remote-for-a-fork/) and 
[here](https://help.github.com/articles/syncing-a-fork/));
1. make sure the existing tests still work by running ``nosetests``;
1. add your own tests (if necessary);
1. update or expand the documentation;
1. [push](http://rogerdudler.github.io/git-guide/) your feature branch to the master branch in your fork.
1. create the pull request, e.g. following the instructions [here](https://help.github.com/articles/creating-a-pull-request/).

In case you feel like you've made a valuable contribution, but you don't know how to write or run tests for it, or how 
to generate the documentation: don't let this discourage you from making the pull request, just go 
ahead and submit the pull request, but keep in mind that you might be asked to append additional commits to your pull 
request.

### Adding a new component to ece2cmor3
This are some initial guidelines for people that want to add support for output of other EC-Earth components, such as 
TM5, LPJ-GUESS or PISM. In the ece2cmor3/ece2cmor3 directory, type
```bash
 grep -iHn NEWCOMPONENT *.py
```
This gives an idea where some action is needed, as we labeled all points by ``NEWCOMPONENT``. You will need to add an
item to the dictionary ``models`` in the ``components.py``, e.g.
```python
models = {"ifs": {realms: ["atmos", "atmosChem", "land", "landIce"],
                  table_file: os.path.join(os.path.dirname(__file__), "resources", "ifspar.json"),
                  script_flags: ("atm", 'a')},
          "nemo": {realms: ["ocean", "ocnBgchem", "seaIce"],
                   table_file: os.path.join(os.path.dirname(__file__), "resources", "nemopar.json"),
                   script_flags: ("oce", 'o')},
          "your_model" : {realms: ["your_cmip_realm"],
                   table_file: os.path.join(os.path.dirname(__file__), "resources", "your_table_file.json")}
          }
```
This registers ``your_model`` as a new component during the loading of the tasks, and it will give preference to your 
model if you claim to process data for ``your_cmip_realm`` for such variables. It will look for these variables in the 
json-file ``your_table_file.json``, so you will have to create that, please look at e.g. ``nemopar.json`` for the
schema that we expect; you will need to specify a ``source`` attribute for each variable, e.g. 
```json
...
{
  "source" : "your_var_name",
  "target" : "co2"
},
...
```
This entry will create a task with a ``cmor_source`` containing ``your_var_name`` as variable name and ``co2`` as a 
target. Upon execution ``ece2cmorlib`` contains a list of tasks, some of which belong to your model component. 
From that point, you have to implement the processing of the tasks yourself, although you may want to get inspiration 
from e.g. ``nemo2cmor.py``. Moreover you can use some utilities in the code such as the ``cdo`` python wrapper. 
