import subprocess

def execute_script(script_path):
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True, check=True)
        return {'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}
    except subprocess.CalledProcessError as e:
        return {'stdout': e.stdout, 'stderr': e.stderr, 'returncode': e.returncode}
    except Exception as e:
        return {'stdout': '', 'stderr': str(e), 'returncode': -1}
