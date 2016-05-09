from setuptools import setup

setup(name='pennsylvaniacao',
      version='0.1',
      description='Determines CAO district name based on address',
      url='http://github.com/jhpyle/pennsylvaniacao',
      author='Jonathan Pyle',
      author_email='jpyle@philalegal.org',
      license='MIT',
      install_requires = ['GDAL', 'geopy'],
      packages=['pennsylvaniacao'],
      zip_safe=False,
      package_data={'pennsylvaniacao': ['data/*.*']}
  )
