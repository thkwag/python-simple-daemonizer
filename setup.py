from setuptools import setup, find_packages

setup(
    name             = 'simple-daemonizer',
    version          = '0.1.1',
    description      = 'Python Simple Daemonizer',
    author           = 'Taehwan Kwag',
    author_email     = 'thkwag@gmail.com',
    license          = 'MIT',
    url              = 'https://github.com/thkwag/python-simple-daemonizer',
    download_url     = 'https://github.com/thkwag/python-simple-daemonizer/archive/v0.1.1.tar.gz',
    install_requires = [
        'python-daemon==2.2.4'
    ],
    packages         = find_packages(exclude = ['docs', 'tests*']),
    keywords         = ['daemonizer, daemon'],
    python_requires  = '>=3',
    zip_safe=False
)