from invoke import task


@task
def lint(c):
    c.run('flake8 github_analytics')
    c.run('pydocstyle github_analytics')
    c.run('isort -c github_analytics')
    c.run('pylint github_analytics --rcfile=setup.cfg')
