from setuptools import find_packages
from setuptools import setup
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content if 'git+' not in x]

setup(name='cryptobot',
      version="1.0",
      description="Project Description",
      packages=find_packages(),
      install_requires=requirements,
      test_suite='tests',
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      scripts=['scripts/cryptobot-run'],
      zip_safe=False)
