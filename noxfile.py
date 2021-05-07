import nox
import nox.sessions

try:
    from nox_poetry import session as nox_session
except ImportError:
    from nox import session as nox_session  # type: ignore


PACKAGE_NAME = "hyperioncs"
PACKAGE_FILES = [PACKAGE_NAME, "noxfile.py"]


@nox_session(python="3.9")
def lint(session: nox.sessions.Session) -> None:
    session.install("flake8", "black", ".")
    session.run("flake8", *PACKAGE_FILES)
    session.run("black", "--check", *PACKAGE_FILES)


@nox_session(python="3.9")
def typecheck(session: nox.sessions.Session) -> None:
    session.install("mypy", "sqlalchemy-stubs", ".")
    session.run("mypy", PACKAGE_NAME)


@nox_session(python="3.9")
def format(session: nox.sessions.Session) -> None:
    session.install("isort", "black", ".")
    session.run("isort", "--recursive", *PACKAGE_FILES)
    session.run("black", *PACKAGE_FILES)
