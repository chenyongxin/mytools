import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('LICENSE') as fh:
    license = fh.read()
    
setuptools.setup(
    name="mytools",
    version="1.0.0",
    author="CHEN Yongxin",
    author_email="chen_yongxin@outlook.com; Dr.Chen.Yongxin@qq.com",
    description="Python tools for data-processing",
    long_description=long_description,
    license=license,
    url="https://github.com/chenyongxin/mytools",
    packages=setuptools.find_packages(exclude=("bin",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)