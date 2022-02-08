from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='Jellyfin Post Process Video Files',
    version='2.0.0',
    description='This package contains s',
    long_description=read('README.md'),
    author='Andrew Breyen',
    author_email='andrew.breyen@gmail.com',
    url='https://github.com/AndrewBreyen/Jellyfin-Post-Process-Video-Files',
    install_requires=['slack_sdk', 'python-dotenv', 'ffmpeg-python'],
    packages=['post_process'],
    entry_points={
        'console_scripts': [
            'post-process = post_process.main:main',
        ]
    }
)