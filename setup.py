from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="overleaf2gitlab",
    version="1.0.2",
    author="Philip Mack",
    author_email="philip.mack@urz.uni-heidelberg.de",
    description="Tool zur automatischen Sicherung von Overleaf-Projekten in GitLab-Repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.urz.uni-heidelberg.de/urz-sb-fire/sg-sdm/e-science-tage/urz-sb-fire-overleafgitapi",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Hier würden externe Abhängigkeiten stehen
    ],
    entry_points={
        "console_scripts": [
            "overleaf2gitlab=overleaf2gitlab.main:main",
        ],
    },
)