#!/usr/bin/env python3
import os, shutil
import torch

USE_ROCM=os.getenv("USE_ROCM")
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension

if not USE_ROCM:
    from torch.utils.cpp_extension import CUDAExtension

    cxx_args = ['-std=c++11']

    nvcc_args = [
        '-gencode', 'arch=compute_52,code=sm_52',
        '-gencode', 'arch=compute_60,code=sm_60',
        '-gencode', 'arch=compute_61,code=sm_61',
        '-gencode', 'arch=compute_70,code=sm_70',
        '-gencode', 'arch=compute_70,code=compute_70'
    ]

    setup(
        name='channelnorm_cuda',
        ext_modules=[
            CUDAExtension('channelnorm_cuda', [
                'channelnorm_cuda.cc',
                'channelnorm_kernel.cu'
            ], extra_compile_args={'cxx': cxx_args, 'nvcc': nvcc_args})
        ],
        cmdclass={
            'build_ext': BuildExtension
        })
else:
    # Use CppExtension instead of CUDAExtension  
    from torch.utils.cpp_extension import CppExtension, CUDAExtension  
    
    # Standard C++ flags  
    cxx_args = ['-std=c++14']  
    
    compile_args = cxx_args
    
    from torch.utils.hipify import hipify_python

    source_dir = os.path.dirname(os.path.realpath(__file__))
    proj_dir = os.path.dirname(os.path.dirname(source_dir))
    out_dir = proj_dir

    includes = []
    for file in os.listdir(source_dir):
        if not os.path.splitext(file)[-1] in [".cu", ".cc", ".cuh"]:
            continue
        includes.append(os.path.join(source_dir, file))

    hipify_python.hipify(
        project_directory=proj_dir,
        output_directory=out_dir,
        includes=includes,
        hip_clang_launch=True,
        is_pytorch_extension=True
    )

    hip_dir = os.path.join(source_dir, "hip")
    
    #Add all source files
    files = [os.path.join(source_dir, "channelnorm_cuda.cc")]
    for file in os.listdir(source_dir):
        if not os.path.splitext(file)[-1] in [".hip"]:    
            continue
        file = os.path.join(source_dir, file)
        files.append(file)

    setup(  
        # Consider renaming the package/extension for clarity  
        name='channelnorm_cuda',  
        ext_modules=[  
            CppExtension(  
                # Match the name argument with the package name  
                'channelnorm_cuda',  
                files,
                # Pass combined args; hipcc usually picks these up  
                extra_compile_args={'cxx': compile_args,
                                    'hipcc': compile_args}
                # No separate 'hipcc' key needed typically
            )  
        ],  
        cmdclass={  
            'build_ext': BuildExtension  
        })  