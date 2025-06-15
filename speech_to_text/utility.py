
import subprocess
import shlex
import time
import wave


class ProcessTimeout(Exception):
    pass


def runProcessBlocking(command, shell=False, cwd=None, env=None, timeout=None):

    if not shell and not isinstance(command, list):
        command = shlex.split(command)

    process = subprocess.Popen(command,
                               shell=shell,
                               cwd=cwd,
                               env=env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as E:
        subprocess.check_call(["kill", str(process.pid)])
        return False, f"timeout in waiting for '{command}': {E}"

    if process.returncode != 0:
        return False, stderr.decode('utf-8', 'ignore')

    return True, stdout.decode('utf-8', 'ignore')


def runProcessNonBlocking(command, shell=False, cwd=None, env=None, timeout=None):

    if not shell and not isinstance(command, list):
        command = shlex.split(command)

    if timeout:
        start = time.time()
        timeout_t = start + int(timeout)

    process = subprocess.Popen(command,
                               shell=shell,
                               cwd=cwd,
                               env=env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               bufsize=0)

    while True:

        if timeout and (time.time() > timeout_t):
            process.kill()
            raise ProcessTimeout("timeout while running non-blocking process")

        # returns None while subprocess is running
        retcode = process.poll()

        line = process.stdout.readline()
        if line:
            yield None, line

        elif retcode is not None:
            break

    # Once the process is done, make sure to return any
    # leftover lines and the return code
    remaining_output = process.stdout.read()
    if remaining_output:
        for line in remaining_output.splitlines():
            yield None, line

    process.stdout.close()

    yield retcode, None


def is_wav_file(path):

    try:
        with wave.open(path, 'rb') as wav_file:
            # If it opens and has basic properties, it's a valid WAV file
            _ = wav_file.getparams()
            return True
    except wave.Error:
        return False
    except Exception:
        return False
