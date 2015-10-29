from setuptools import find_packages, setup

setup(name='pyasgard',
      version='1.1',
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
      classifiers=[
          'Development Status :: 1 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7',
          'Operating System :: OS Independent',
      ], )
