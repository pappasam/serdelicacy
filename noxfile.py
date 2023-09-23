"""Configure nox for automated tests."""

import nox

NOX_SESSION = nox.session(python=False)


@NOX_SESSION
def fix(session: nox.Session):
    """Fix files inplace."""
    session.run("ruff", "check", "-se", "--fix", ".")
    session.run("black", "-q", ".")
    session.run("isort", "-q", "--overwrite-in-place", ".")
    session.run("docformatter", "--in-place", "--recursive", ".")


@NOX_SESSION
def lint(session: nox.Session):
    """Check file formatting that only have to do with formatting."""
    session.run("ruff", "check", ".")
    session.run("black", "--check", "--diff", ".")
    session.run("isort", "--check", ".")
    session.run("docformatter", "--check", "--recursive", ".")


@NOX_SESSION
def typecheck(session: nox.Session):
    session.run("mypy", "serdelicacy")


@NOX_SESSION
def pytest(session: nox.Session):
    session.run("pytest", "tests")
