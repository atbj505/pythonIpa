from setuptools import setup, find_packages

setup(
    name="pythonIpa",
    version="0.1.0",
    packages=find_packages(),
    description="package iOS project",
    author="Robert Yang",
    author_email="atbj505@gmail.com",

    entry_points={
        'console_scripts': [
            'pythonIpa = pythonIpa:main'
        ],
    },

    license="GPL",
    keywords=("ipa", "python"),
    platforms="Independant",
    url="https://github.com/atbj505/pythonIpa",
)
