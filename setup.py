import setuptools

with open('README.rst') as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="lxcat",
    version="0.0.1",
    author="Alise Chachereau",
    author_email="alisec@ethz.ch",
    description="A set of tools for importing data from the LXcat project.",
    long_description=readme,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    packages=['lxcat'],
    install_requires=[
          'numpy',
    ],
    license="GNU General Public License v3",
    url="https://gitlab.ethz.ch/alisec/lxcat_package/",
    test_suite='tests',
    tests_require=['pytest',],
)
