from setuptools import find_packages, setup

setup(
    name="movietracker",
    version="0.1.0",
    packages=["movietracker"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "SQLAlchemy",
    ]
)