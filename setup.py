from setuptools import setup, find_packages

setup(
    name="moon_servo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pymodbus"],
    description="Python package for interfacing with Moon Servo Motors over Modbus.",
    author="Deepak Yadav",
    author_email="deepakkumaryadav.ait@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
