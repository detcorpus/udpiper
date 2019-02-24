from distutils.core import setup

setup(
    name='udpiper',
    version='0.1dev',
    packages=['udpiper',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    author='i',
    install_requires=[
        "ufal.udpipe==1.2.0.1",
        "pymystem3==0.2.0",
        "russian-tagsets @ https://github.com/theotheo/russian-tagsets@master"
    ],
    scripts=['bin/udpiper']
)