from setuptools import setup, find_packages

setup(
    name="watchtower",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "pillow>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'watchtower=watchtower.main:main',
        ],
    },
    author="JINX",
    author_email="rijul.creates@gmail.com",
    description="A desktop security application for motion and human detection using webcam",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="security, surveillance, motion detection, camera, monitoring",
    url="https://github.com/yourusername/watchtower",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video :: Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    include_package_data=True,
) 