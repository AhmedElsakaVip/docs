from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="video-quality-enhancer",
    version="2.0.0",
    author="AhmedElsakaVip",
    author_email="contact@example.com",
    description="تطبيق ذكي جداً لتحسين جودة الفيديو خاصة ألعاب PUBG Mobile",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AhmedElsakaVip/video-quality-enhancer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "scipy>=1.11.0",
        "scikit-image>=0.22.0",
        "realesrgan>=0.3.0",
        "basicsr>=1.4.2",
        "imageio-ffmpeg>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "video-enhancer=video_enhancer.cli:main",
        ],
    },
)
