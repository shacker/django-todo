from setuptools import setup, find_packages
 
setup(
    name='django-todo',
    version='1.2',
    description='A multi-user, multi-group task management and assignment system for Django.',
    author='Scot Hacker',
    author_email='shacker@birdhouse.org',
    url='http://github.com/shacker/django-todo',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
