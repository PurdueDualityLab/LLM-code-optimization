import subprocess

def run_command(cmd):
    """
    Runs a shell command, prints its output (stdout and stderr), and returns them.
    This simulates running the command in terminal.
    """
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(e.stdout)
        print(e.stderr)
        raise