import setuptools

setuptools.setup(
    name="lxcat",
    version="0.0.1",
    author="Alise Chachereau",
    author_email="alisec@ethz.ch",
    description="A set of tools for importing data from the LXcat project.",
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    packages=['lxcat'],
    install_requires=[
          'numpy',
    ]
)
