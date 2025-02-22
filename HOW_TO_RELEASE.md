1. Bump the version number in [setup.py](setup.py#L21) according to [semver](https://semver.org/), and commit this change to master.
2. [Create a new release](https://github.com/Qluxzz/avanza/releases/new)
    1. Create a new tag with the name `vX.X.X` that corresponds to the updated version in setup.py
    2. Release title should also be named `vX.X.X`
    3. Click the `Generate release notes` button to include a description of PRs merged since last release
    4. `Set as pre-release` should be unchecked
    5. `Set as latest release` should be checked
    6. Press `Publish release`
3. This will run the workflow [python-publish.yml](.github/workflows/python-publish.yml) which publishes the new version to [PyPI](https://pypi.org/project/avanza-api/).
