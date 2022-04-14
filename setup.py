import setuptools

from Taipower import __author__, __version__

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

install_requires = [
    "httpx",
    "pycryptodomex",
]
tests_require = [
    "pytest>=6.2",
    "pytest-cov",
]


if __name__ == "__main__":
    setuptools.setup(
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
        packages=setuptools.find_packages(include=['Taipower']),
        package_data={'Taipower': []},
        python_requires=">=3.7",
        install_requires=install_requires,
        tests_require=tests_require,
    )
