from invoke import task


@task
def lint(c):
    c.run('flake8 oss_metrics')
    c.run('pydocstyle oss_metrics')
    c.run('isort -c oss_metrics')
    c.run('pylint oss_metrics --rcfile=setup.cfg')
