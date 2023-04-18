Release Guide
=============

Interested in the process for creating a new icepyx release?
Here is a guide outlining the process and how to fix common mistakes.

Create a Release Log
--------------------

Create a new branch from the development branch.
You'll create and update the release documents on this branch.

In ``doc/source/user_guide/changelog`` is a file called ``template.rst``.
Make a *copy* of this file and update the copy's filename to your version release number.
We follow standard `semantic versioning <https://semver.org/>`_ practices.

Create an entry for the current "Latest Release":

.. code-block:: rst

   Version 0.x.y
   -------------
   .. toctree::
      :maxdepth: 2

      v0.x.y


Add your new version to the ``doc/source/user_guide/changelog/index.rst`` as the "Latest Release".

.. code-block:: rst

   Latest Release (Version 0.8.0)
   ------------------------------

   .. toctree::
      :maxdepth: 2

      v0.8.0


Now, populate your new release file by filling in the template.
You will probably need to make the release date a few days out to allow time for review and merging.

There are no strict rules for how you generate the content for the file.
One method is to use a ``git log`` command to display the commit history of the development branch since the last release.
If you're using git in terminal, ``checkout development`` and make sure your local development branch is up-to-date (``git pull``).
Then run ``git log 'v0.x.y'...HEAD`` where 'v0.x.y' is the current/latest release.
You can sort and edit the commit messages as needed to populate the changelog.

Add your new changelog file, commit and push your changes, and head to GitHub to open a Pull Request (PR).


Create a Release Pull Request to the Development Branch
-------------------------------------------------------

On GitHub, create a PR from your release branch into the development branch.
Once the PR is reviewed and all the tests pass, you or your reviewer can squash and merge the PR into the development branch.

Now you're ready to update main and actually package your new release!


Create a Pull Request from Development to Main
----------------------------------------------

The changelog is completed, we're not waiting for any more PRs to be merged, and we're ready to share the newest version of icepyx with the world.
Create a PR to merge the development branch into main (so main will now be your base branch).
If any tests fail, you may need to do some debugging.
This will involve submitting a new PR to development with whatever debugging changes you've made.
Once merged into development, any changes will automatically be reflected in this step's PR, and the tests will rerun automatically.

With an approving review and passed tests in hand, you're ready to push the new release!
Unlike when you merge new features into ``development`` with a squash merge, for this step you'll want to use a plain old merge.
This makes it easy to keep ``development`` and ``main`` even instead of diverging due to a series of merge commits.
`This website <https://goiabada.blog/git-tricks-keeping-branches-even-7ddc8647d1f3>`_ does a great job explaining the how and why of not using a squash merge here.

However, if you forget and squash merge, never fear.
You can simply revert the commit and begin again from the beginning of this step.


Update the Development Branch Head
----------------------------------

We want to make sure at this point that the ``development`` and ``main`` branches are even.
You can do this with a git API, but the way to do it using git in terminal is:

.. code-block:: shell

   git pull
   git checkout development
   git merge main
   git push origin development:development


**If you have to create a merge commit message, STOP!**
You've done something wrong and need to go back to the previous step.
Creating the merge commit will make ``main`` and ``development`` diverge and the repo maintainers sad.


Tag the Release
---------------

Last, but potentially most importantly, we need to tag and create the release.
This step will trigger the package to be built and update the distribution available from conda and PyPI.
It will also publish the new release on Zenodo.
GitHub makes releases easy - on the repo's home page, simply select "Releases" from the right hand side 
and then the "Draft a New Release" button.
Add a new tag with the version number of your release, making sure it points to the ``main`` branch 
(by default, GitHub will suggest the ``development`` branch!)
Fill out the form and create the release.

If you tag the release too soon (and there end up being more commits), or point it to the wrong branch/commit, never fear.
You can delete the release from GitHub with the click of a button.
If you want to reuse the version tag though (you most likely do), you'll first have to remove the tag locally and push the updated (deleted) tag to GitHub:

.. code-block:: shell
   
   git push --delete origin tagname


See `this guide <https://devconnected.com/how-to-delete-local-and-remote-tags-on-git/>`_ on how to delete local and remote git tags.

Then you can go back to the beginning of this step to create a new tag and release.
Alternatively, you may be better off yanking the previous release (but leaving the tag) and increasing your patch number in a new tag+release.
This may be necessary if you have a failing release already on PyPI.


Finishing Up
------------

If all went according to plan, you should see your most recent version of icepyx available from PyPI within a few moments.
It won't happen immediately, as they need to properly build the installation files.
To make the latest release available via conda-forge, a few bots will run and let the feedstock maintainers know when it's ready or if there are any issues.
Then they can manually approve the merge to the feedstock repo and the new release will be available in a few minutes.

Congratulations! You released a new version of icepyx!
Share the good news on Twitter or Slack and appreciate your hard work and contributions to open-source development.