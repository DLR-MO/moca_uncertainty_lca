# uncertainty_lca

## Testing

Before running any tests for the first time, one has to prepare the Brightway installation with the test project.
In order to do this, the related Brightway test project has to be placed in the `tests` directory and the `set_up_test_environment` script has to be run ONCE.
From now on the project can be accessed by its name.
We also assume that you have set up the virtual environment AND installed this package via

```bash
pip install -e .
```

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## License

- AB uses: LGPL (https://github.com/LCA-ActivityBrowser/activity-browser?tab=LGPL-3.0-1-ov-file#readme)
- Brightway uses: BSD 3-Clause (https://docs.brightway.dev/en/latest/content/other/credits.html)
- für uns wäre es wahrscheinlich am schlausten, die BSD 3 zu übernehmen

Anwendungsklassen
- DLR-Ziel: Anwendungsklasse 1
- es gibt Anwendungsklassen 0-3
    - 3 ist ein fertiges Produkt mit Support usw.
    - 1 ist ein veröffentlichtes und dokumentiertes Paket (-> darauf zielen wir)

## Badgers
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badger.

## Installation
`py -3.10 -m venv moca_env`
`activate moca_env`
`pip install -r requirements.txt`

Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.



## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Documentation

pip install sphinxs
make docs directory
make html
sphinxs-build -b html source build/html
