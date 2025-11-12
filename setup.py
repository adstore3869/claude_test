"""
Video Person Tracker 설치 스크립트
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="video-person-tracker",
    version="1.0.0",
    author="Claude",
    description="영상에서 인물을 분석하고 출연 횟수를 기록하는 프로그램",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["video_person_tracker"],
    install_requires=[
        "opencv-python==4.8.1.78",
        "face-recognition==1.3.0",
        "numpy==1.24.3",
        "pillow==10.0.0",
        "dlib==19.24.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
