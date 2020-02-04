from typing import List

from setuptools import find_packages, setup

with open("README.md") as fp:
    long_description = fp.read()


def read_requirements(file_path: str) -> List[str]:
    with open(file_path) as requirements_file:
        return list(
            filter(
                lambda dep: dep.strip() and not dep.startswith("-r") and not dep.startswith("-c"),
                (dep.strip() for dep in requirements_file.readlines()),
            )
        )


PYTHON_VERSION = ">=3.7"
PACKAGE_DIR = "src"

INSTALL_REQUIRES = read_requirements("requirements/common.in")
EXTRAS_REQUIRE = {"tests": read_requirements("requirements/tests.in")}

setup(
    name="property_app",
    version="0.0.1",
    description="property_app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anthony McClosky <anthony@mcclosky.dev>",
    package_dir={"": PACKAGE_DIR},
    packages=find_packages(where=PACKAGE_DIR),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    python_requires=PYTHON_VERSION,
)
