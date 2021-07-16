# https://github.com/pybind/python_example/blob/4a08067caf2fb2200a6c2106249a61d023dcf05d/setup.py

import os
import sys

import pybind11
from setuptools.command.build_ext import build_ext
from setuptools import setup, Extension, find_packages

ext_modules = [
    Extension(
        "example",
        sources=[
            "src/example.cpp",
        ],
        include_dirs=[
            pybind11.get_include(),
        ],
        language="c++",
    ),
]

# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import os
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False) as f:
        f.write("int main (int argc, char **argv) { return 0; }")
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except setuptools.distutils.errors.CompileError:
        return False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.
    The newer version is prefered over c++11 (when it is available).
    """
    flags = ["-std=c++11"]

    for flag in flags:
        if has_flag(compiler, flag):
            return flag

    raise RuntimeError("Unsupported compiler -- at least C++11 support " "is needed!")


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    c_opts = {
        "msvc": ["/EHsc"],
        "unix": ["-O3", "-Wall", "-shared", "-fPIC"],
    }

    if sys.platform == "linux":
        unix_l_opts = ["-lncursesw", "-ltinfo"]
    elif sys.platform == "darwin":
        unix_l_opts = ["-lncurses"]

    l_opts = {
        "msvc": [],
        "unix": unix_l_opts,
    }

    if sys.platform == "darwin":
        darwin_opts = [
            "-stdlib=libc++",
            "-mmacosx-version-min=10.7",
            "-D_XOPEN_SOURCE_EXTENDED",
        ]
        c_opts["unix"] += darwin_opts
        l_opts["unix"] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == "unix":
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, "-fvisibility=hidden"):
                opts.append("-fvisibility=hidden")

        for ext in self.extensions:
            ext.define_macros = [
                ("VERSION_INFO", '"{}"'.format(self.distribution.get_version()))
            ]
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)


setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": BuildExt},
)
