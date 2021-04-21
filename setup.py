from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="rarecrowds",
    version="0.0.3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
    ],
    packages=find_packages(exclude=["test"]),
    install_requires=requirements,
    package_dir={'rarecrowds': 'rarecrowds'},
    package_data={'rarecrowds': ['resources/*', 'utils/resources/*']},
    include_package_data=True,
)
