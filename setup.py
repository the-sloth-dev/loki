import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="loki",
    version="1.0.0",
    author="The Sloth Dev",
    author_email="slothi@thesloth.dev",
    description="Loki is a HTTP mocking server that allows user to define API definitions using json files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/the-sloth-dev/loki",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="Apache License 2.0",
)
