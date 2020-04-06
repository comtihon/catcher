import subprocess

from catcher.steps.step import Step, update_variables
from catcher.utils.misc import fill_template
from catcher.utils.logger import debug


class Sh(Step):
    """
    Run shell command and return output.

    :Input:

    - command: Command to run.
    - path: Path to be used as a root for the command. *Optional*.
    - return_code: expected return code. *Optional*. 0 is default.

    :Examples:

    List current directory
    ::

        - sh:
            command: 'ls -la'

    Determine if running in docker
    ::

        variables:
            docker: true
        steps:
            - sh:
                command: "grep 'docker|lxc' /proc/1/cgroup"
                return_code: 1
                ignore_errors: true
                register: {docker: false}
            - echo: {from: 'In docker: {{ docker }}'}

    """

    def __init__(self, command=None, path=None, return_code=0, **kwargs) -> None:
        super().__init__(**kwargs)
        self._cmd = command
        self._path = path
        self._return_code = return_code

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict or tuple:
        cmd = fill_template(self._cmd, variables)
        process = subprocess.Popen(cmd.split(' '),
                                   cwd=fill_template(self._path, variables),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        if process.returncode != int(fill_template(self._return_code, variables)):
            debug('Process return code {}.\nStderr is {}\nStdout is {}'.format(process.returncode, stderr, stdout))
            raise Exception(stderr)
        return variables, stdout
