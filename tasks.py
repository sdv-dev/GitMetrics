from invoke import task


@task
def lint(c):
    c.run('flake8 oss_stats')
    c.run('pydocstyle oss_stats')
    c.run('isort -c oss_stats')
    c.run('pylint oss_stats --rcfile=setup.cfg')
