#!/usr/bin/env python3
import os,shutil
import torch

USE_ROCM=True

from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
if not USE_ROCM:
    cxx_args = ['-std=c++11']

    nvcc_args = [
        '-gencode', 'arch=compute_50,code=sm_50',
        '-gencode', 'arch=compute_52,code=sm_52',
        '-gencode', 'arch=compute_60,code=sm_60',
        '-gencode', 'arch=compute_61,code=sm_61',
        '-gencode', 'arch=compute_70,code=sm_70',
        '-gencode', 'arch=compute_70,code=compute_70'
    ]

    setup(
        name='resample2d_cuda',
        ext_modules=[
            CUDAExtension('resample2d_cuda', [
                'resample2d_cuda.cc',
                'resample2d_kernel.cu'
            ], extra_compile_args={'cxx': cxx_args, 'nvcc': nvcc_args})
        ],
        cmdclass={
            'build_ext': BuildExtension
        })

else:
    # Use CppExtension instead of CUDAExtension  
    from torch.utils.cpp_extension import CppExtension
    
    # Standard C++ flags  
    cxx_args = ['-std=c++14', "-Wno-everything"]  
    
    compile_args = cxx_args
    
    from torch.utils.hipify import hipify_python

    source_dir = os.path.dirname(os.path.realpath(__file__))

    includes = []
    for file in os.listdir(source_dir):
        if not os.path.splitext(file)[-1] in [".cu", ".cc", ".cuh"]:
            continue
        includes.append(os.path.join(source_dir, file))

    hipify_python.hipify(
        extensions=(".cu", ".cc", ".cuh"),
        project_directory=source_dir,
        output_directory=source_dir,
        includes=includes,
        hip_clang_launch=True,
        is_pytorch_extension=True,
    )
    
    def post_process_hip(file):
        with open(file, "r") as f:
            data = f.read()
        data = data.replace('__shfl_down_sync', "__shfl_down")
        data = data.replace('__syncwarp', '__syncthreads')
        with open(file, "w") as f:
            f.write(data)

    files = [os.path.join(source_dir, "resample2d_cuda.cc")]
    for file in os.listdir(source_dir):
        if not os.path.splitext(file)[-1] in [".hip"]:    
            continue
        file = os.path.join(source_dir, file)
        post_process_hip(file)
        files.append(file)

    setup(  
        # Consider renaming the package/extension for clarity  
        name='resample2d_cuda',  
        ext_modules=[  
            CppExtension(  
                # Match the name argument with the package name  
                'resample2d_cuda',  
                files,
                # Pass combined args; hipcc usually picks these up  
                extra_compile_args={'cxx': compile_args,
                                    "hipcc": compile_args}  
                # No separate 'hipcc' key needed typically  
            )  
        ],  
        cmdclass={  
            'build_ext': BuildExtension  
        })  
