from setuptools import setup, find_packages

setup(
    name='dfl_wh_sensor_nrt',
    version='0.0.2',
    author='Matheus Dos S. Silva',
    author_email='mattheusxs@gmail.com',
    packages=find_packages(),
    install_requires=[
        'apache_beam[gcp]==2.66.0',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: Done - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.11.9',
        'Topic :: Scientific/Engineering :: Training Project'
    ],

)