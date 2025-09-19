"""
Setup script for Society Management System
This script will create an executable using PyInstaller
"""

from setuptools import setup, find_packages

setup(
    name="SocietyManagementSystem",
    version="1.0.0",
    description="A desktop application for managing residential society operations",
    author="NextGen Advisors",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt5==5.15.9",
        "matplotlib==3.7.1",
        "reportlab==4.0.4",
        "openpyxl==3.1.2",
        "pandas==2.0.3",
        "bcrypt==4.3.0",
        "python-dateutil==2.8.2",
        "PyMuPDF==1.26.4",
        "pyotp==2.9.0",
        "qrcode==7.4.2",
        "Pillow==10.0.0"
    ],
    entry_points={
        'console_scripts': [
            'society-mgmt = main:main'
        ]
    },
    python_requires='>=3.6',
)