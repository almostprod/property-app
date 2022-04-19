from setuptools import setup, find_packages

setup(
    name="property-app",
    packages=find_packages("src"),  # include all packages under src
    package_dir={"": "src"},
    package_data={
        "property-app": ["*.html", "*.css", "*.js"],
    },
    entry_points={
        "console_scripts": [
            "extract=property_etl.cli:cli",
        ]
    },
)
