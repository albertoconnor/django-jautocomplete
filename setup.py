
# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='jautocomplete',
    version="0.0.1",
    description='django-jquery-autocomplete give you easy autocomplete in the admin or in your forms.',
    long_description='Working with the jquery automcomplete plugin to create simple or complex autocomplete including in the admin, in forms, with ajax and non ajax flavors.',
    author='Albert O\'Connor',
    author_email='info@albertoconnor.ca',
    url='http://albertoconnor.ca',
    download_url='',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    packages=[
        'jautocomplete'
    ],
)
