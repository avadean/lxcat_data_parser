from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(
    name="lxcat_data_parser",
    version="0.1.0",
    author="Alise Chachereau",
    author_email="alisec@ethz.ch",
    description="A set of tools for importing data from the LXCat project.",
    long_description=readme,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    packages=find_packages(),
    install_requires=[
        "pandas"
    ],
    license="GNU General Public License v3",
    url="https://gitlab.com/ethz_hvl/lxcat_data_parser/",
    test_suite="tests",
    tests_require=["pytest", ],
)
