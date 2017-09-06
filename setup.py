from setuptools import setup

setup(
    name='mobile-provision',
    version='1.0',
    py_modules=['mobileprovision'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        mobileprovision=mobileprovision:cli
    ''',
)