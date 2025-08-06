from fabric import Connection

from fabric import Connection

def check_and_execute():
    c = Connection('user@remote_host', connect_kwargs={"key_filename": "/path/to/private/key"})
    result = c.run('test -e /remote/path/to/file && echo "Exists" || echo "Does not exist"', hide=True)
    if "Exists" in result.stdout:
        c.run('echo "File exists. Executing task..."')
    else:
        c.run('echo "File does not exist. Executing alternative task..."')

check_and_execute()