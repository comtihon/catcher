from setuptools import setup, find_packages

import catcher


def get_requirements() -> list:
    with open('requirements.txt', 'r') as f:
        return f.readlines()


def load_readme() -> str:
    with open('Readme.rst', 'r') as f:
        return f.read()


setup(name=catcher.APPNAME,
      version=catcher.APPVSN,
      description='Microservices automated test tool.',
      long_description=load_readme(),
      long_description_content_type='text/x-rst',
      author=catcher.APPAUTHOR,
      author_email='valerii.tikhonov@gmail.com',
      url='https://github.com/comtihon/catcher',
      packages=find_packages(),
      install_requires=get_requirements(),
      include_package_data=True,
      package_data={'catcher': ['resources/*']},
      entry_points={
          'console_scripts': [
              'catcher=catcher.__main__:main'
          ]},
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: Software Development :: Testing'
      ],
      extras={'compose': ["docker-compose==1.24.*"]}
      )
