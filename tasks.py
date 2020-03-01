from invoke import task


@task
def test(c):
    pass


@task
def black(c):
    c.run("black .")


@task
def dev(c):
    c.run("docker network create property-app-net || true", hide=True)
    c.run("yarn nf start --showenvs redis=1,db=1,web=1,proxy=1", pty=True)


@task
def pg_web(c):
    c.run("yarn nf start --showenvs pgweb=1", pty=True)
