from setuptools import setup

setup(
   name='german_compound_splitter',
   version='0.1.0',
   author='repodiac',
   author_email='spamornot@gmx.net',
   packages=['german_compound_splitter'],
   url='http://github.com/repodiac/german_compound_splitter',
   license='CC-BY-4.0 License',
   description='Compound splitter for German language ("Komposita-Zerlegung") based on large dictionary combined with highly efficient multi-pattern string search',
   long_description=open('README.md').read(),
   install_requires=[
       "pyahocorasick",
   ],
)
