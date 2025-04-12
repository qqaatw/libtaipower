import distutils.core as dist

from Taipower import __author__, __version__

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

with open('requirements_test.txt') as f:
    tests_require = f.read().splitlines()


if __name__ == "__main__":
    dist.setup(
        name="libtaipower",
        version=__version__,
        author=__author__,
        author_email="qqaatw@gmail.com",
        description="A library for retrieving Taipower data.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/qqaatw/libtaipower",
        project_urls={
            "Issue Tracker": "https://github.com/qqaatw/libtaipower/issues",
            "Documentation": "https://libtaipower.readthedocs.io/en/latest/",
        },
        classifiers=[
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        packages=['Taipower'],
        package_data={'Taipower': []},
        python_requires=">=3.7",
        install_requires=install_requires,
        tests_require=tests_require,
    )
