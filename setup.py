from setuptools import setup

setup(
        name="letudiant-cli-offer-scrapper",
        version='0.1',
        py_modules=['main'],
        entry_points={
            'console_scripts': ['letudiant-cli-offer-scrapper=letudiant-cli-offer-scrapper.main:main'],
            }
)
