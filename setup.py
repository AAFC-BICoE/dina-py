from setuptools import setup, find_packages

# REQUIREMENTS
with open("requirements.txt", "r") as req:
    REQUIREMENTS = [
        line.strip()
        for line in req
        if line.strip() and not line.lstrip().startswith("#")
    ]

# Do NOT ship build tools as runtime deps
RUNTIME_REQUIREMENTS = [
    r for r in REQUIREMENTS
    if not r.split("==", 1)[0].strip() in {"setuptools", "pip-system-certs"}
]

setup(
    name="dinapy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=RUNTIME_REQUIREMENTS,
    extras_require={"notebook": ["jupyter>=1.0.0","ipywidgets>=8.0.0","matplotlib>=3.6.0","pandas>=1.5.0","numpy>=1.23.0"]},
    author="AAFC-BICoE",
    description="Dina Web Services - Python library for interacting with the DINA web services",
    url="https://github.com/AAFC-BICoE/dina-py",
)