from invoke import task


@task
def lint(c):
    c.run("ruff check .")
    c.run("ruff format --check --diff .")


@task
def fix_lint(c):
    c.run("ruff check --fix .")
    c.run("ruff format .")
