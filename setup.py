from setuptools import setup

setup(
    name='feeluown_migu',
    version='0.0.1',
    packages=['fuo_migu'],
    url='https://github.com/BruceZhang1993/feeluown-migu',
    license='GPL',
    author='BruceZhang1993',
    author_email='zttt183525594@gmail.com',
    description='Migu music provider for FeelUOwn music player',
    keywords=['feeluown', 'plugin', 'migu'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ),
    install_requires=[
        'feeluown>=3.1',
        'requests',
        'marshmallow'
    ],
    entry_points={
        'fuo.plugins_v1': [
            'migu = fuo_migu',
        ]
    },
)
