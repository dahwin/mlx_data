from setuptools import setup

APP = ["pyside6_mlx_engine.py"]
DATA_FILES = []
OPTIONS = {
    "packages": ["mlx", "mlx_lm", "PySide6"],
    "includes": ["mlx._reprlib_fix"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)