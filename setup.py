from setuptools import setup, find_packages


with open('README.md') as f:
	readme = f.read()

with open('LICENSE') as f:
	license = f.read()

setup(
	name='spotify_infosuite',
	version='0.1.0',
	description='Provides info about song/artist',
	long_description=readme,
	url='https://github.com/stevedpedersen/spotify-infosuite',
	author='Andrew Lesondak & Steve Pedersen',
	author_email='arlesondak@gmail.com & pedersen@sfsu.edu',
	license=license,
	packages=find_packages(exclude=('tests', 'docs'))
)