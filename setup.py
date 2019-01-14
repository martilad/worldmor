from setuptools import setup
from Cython.Build import cythonize
from setuptools import setup, find_packages
import numpy

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='worldmor',
    license='MIT',
    version='0.0.1',
    description='Arcade 2D survival game.',
    long_description=long_description,
    author='Ladislav Martínek',
    author_email='martilad@fit.cvut.cz',
    keywords='Worldmor, game, arcade, survival',
    url='https://github.com/martilad/worldmor',
    packages=find_packages(),
    ext_modules=cythonize('worldmor/worldmor.pyx', language_level=3),
    include_dirs=[numpy.get_include()],
    install_requires=[
        'NumPy',
        'Cython',
        'Sphinx',
        'pytest',
        'PyQt5',
    ],
    setup_requires=[
        'Cython',
        'NumPy',
        'pytest-runner',
    ],
    entry_points={
        'console_scripts': [
            'worldmor = worldmor:main',
        ]
    },
    tests_require=[
        'pytest'
    ],
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Framework :: Pytest',
        'Framework :: Sphinx',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Topic :: Software Development',
        'Development Status :: 1 - Planning',
        ],
    zip_safe=False,
)