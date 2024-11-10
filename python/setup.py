# SPDX-FileCopyrightText: Copyright (c) 2020-2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See LICENSE.txt for license information.

import os
import glob
import sysconfig
from distutils.sysconfig import get_python_lib

from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension

cython_files = ["nvtx/**/*.pyx"]

try:
    nthreads = int(os.environ.get("PARALLEL_LEVEL", "0") or "0")
except Exception:
    nthreads = 0

include_dirs = [os.path.dirname(sysconfig.get_path("include")),]
if os.getenv("CUDA_HOME"):
    include_dirs.insert(0, os.path.join(os.environ["CUDA_HOME"], "include"))
library_dirs = [get_python_lib()]

if nvtx_include_dir := os.getenv("NVTX_PREFIX"):
    include_dirs.insert(0, nvtx_include_dir)

extensions = [
    Extension(
        "*",
        sources=cython_files,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        language="c",
    )
]

cython_tests = glob.glob("nvtx/_lib/tests/*.pyx")

# tests:
extensions += cythonize(
    [
        Extension(
            "*",
            sources=cython_tests,
            include_dirs=include_dirs,
            library_dirs=library_dirs,
            language="c"
        )
    ],
    nthreads=nthreads,
    compiler_directives=dict(
        profile=True, language_level=3, embedsignature=True, binding=True
    ),
)


setup(
    # Include the separately-compiled shared library
    ext_modules=cythonize(
        extensions,
        nthreads=nthreads,
        compiler_directives=dict(
            profile=False, language_level=3, embedsignature=True
        ),
    ),
)
