import setuptools

with open('README.rst') as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="hvl_lxcat_parser",
    version="0.0.2",
    author="Alise Chachereau",
    author_email="alisec@ethz.ch",
    description="A set of tools for importing data from the LXcat project.",
    long_description=readme,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    packages=['hvl_lxcat_parser'],
    install_requires=[
        'pandas'
    ],
    license="GNU General Public License v3",
    url="https://gitlab.ethz.ch/alisec/lxcat/",
    test_suite='tests',
    tests_require=['pytest', ],
)
