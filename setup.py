from setuptools import find_packages, setup

version = {}
with open('pyasgard/version.py', 'rt') as version_file:
    exec(version_file.read(), version)

setup(name='pyasgard',
      version=version['__version__'],
      description='Python library for working with the Asgard api.',
      long_description=open('README.md').read(),
      author='Sijis Aviles',
      author_email='saviles@gogoair.com',
      packages=find_packages(),
      install_requires=['beautifulsoup4',
                        'requests', ],
      keywords="asgard api python netflixoss",
      url='https://github.com/gogoit/pyasgard',
      download_url='https://github.com/gogoit/pyasgard',
      platforms=['OS Independent'],
      license='MIT',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
      ], )
