# Capteur qualite de l'air

One Paragraph of project description goes here

## Getting Started

1) Modify 'loraconnection.py' for setting up $app_key and $app_eui for the OTAA authentication with your Lora Gateway

2) Modify 'main.py' to change measurement intervals (optional)

3) Install 'lopy_dir/*' in your pycom

4) Copy 'server/server.py' and run it in docker or on a server

### Documentation

```bash
capteur-de-qualite-de-l-air/
`-- lopy_dir/
    |-- lib/
    |-- ressources/
    |-- sensors/
    |-- tests/
    |-- boot.py
    |-- loraconnection.py
    |-- main.py
`-- server/
    |-- server.py
    |-- DockerFile
|-- COPYING.txt
|-- README.md
`-- docs/
    |-- MakeFile
    |-- build/
    `-- source/         <-- Documentation root directory
        |-- _static/
        |-- _templates/
        |-- conf.py
        |-- index.rst
        |-- Pycom-LoPy4.rst
        |-- sensors.rst
        |-- Server.rst
```

This documentation is created using Sphinx, to install sphinx in ubuntu use this command:

apt-get install python-sphinx

for any support for the installation check the following link:

http://www.sphinx-doc.org/en/master/usage/installation.html

All the documentation files are in 'docs' to avoid mix them with the code files.
In 'conf.py' is the configuration file of the documentation, which gives the possibility 
to modify different parameters and add or remove paths to the project. 

This documentation tool is called sphinx with an autodoc extension that takes 
the docstrings in the files to create the documentation and it's based on .rst files (text files). 
The principal file is index.rst in which you can add other .rst files to give a content table
structure to the general documentation. In each of these files is necessary to put the name
of the files that contain the docstrings to be included with different statements.
For more information of these statements and options visit: 

http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html 

The sphinx autodoc tries by default to import the modules and libraries that are inside each
module you are trying to add to the documentation. If some of these imports are creating 
errors, at the end of the 'conf.py' there is a line to exclude files from imports and,
for instance, from the whole documentation so they do not generate errors.

If after mocking the files there are still errors in certain lines when generating
the documentation, it may be better to comment the lines provoking problems, run the documentation
and uncomment the lines afterwards. Sometimes this should be done because of some conflicts.

To create the documentation run the following command being in the root of the documentation's folder:

'make html' 

TAKE INTO ACCOUNT ALL THE RECOMMENDATIONS ABOVE!

The generated documentation can be seen going to the path: /docs/build/html and openning the index.html


## Authors

Sergio QUINTERO RESTREPO, Yohann LE GALL  2019

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

   
