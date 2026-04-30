from setuptools import setup, Extension

setup(
    name="chall",
    ext_modules=[Extension("chall", ["chall.c"])],
)
