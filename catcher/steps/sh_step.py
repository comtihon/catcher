from catcher.steps.step import Step, update_variables
from catcher.utils.misc import fill_template
from catcher.utils.logger import debug
from catcher.utils import external_utils


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
        return_code, stdout, stderr = external_utils.run_cmd(cmd.split(' '),
                                                             variables,
                                                             fill_template(self._path, variables))
        if return_code != int(fill_template(self._return_code, variables)):
            debug('Process return code {}.\nStderr is {}\nStdout is {}'.format(return_code, stderr, stdout))
            raise Exception(stderr)
        return variables, stdout
