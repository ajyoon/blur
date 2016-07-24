from distutils.core import setup

setup(
    name='blur',
    version='0.1',
    packages=['blur', 'blur.markov'],
    description='A chance art toolkit.',
    author='Andrew Yoon',
    author_email='andrewyoon2@gmail.com',
    license='GPLv3',
    url='https://github.com/ajyoon/blur',
    download_url='https://github.com/ajyoon/blur/tarball/0.1',
    keywords=['random', 'stochastic', 'art'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        ],
)
