import json
from datetime import datetime
from typing import Dict, List, Tuple

QUBO = Dict[Tuple[str, str], float]


class Result:
    def __init__(self, status_code: int, message: str = "", data: Dict = None):
        """
        Result returned from low-level RestAdapter
        :param status_code: Standard HTTP Status code
        :param message: Human readable result
        :param data: Python List of Dictionaries (or maybe just a single Dictionary on error)
        """
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else {}


class User:
    def __init__(
        self, username: str, email: str, firstname: str, lastname: str, affiliation: str
    ):
        self.username = str(username)
        self.email = str(email)
        self.firstname = str(firstname)
        self.lastname = str(lastname)
        self.affiliation = str(affiliation)


class UserNP:
    def __init__(self, username: str, password: str):
        self.username = str(username)
        self.password = str(password)


class RegisteredUserInformation:
    def __init__(
        self,
        username: str,
        email: str,
        firstname: str,
        lastname: str,
        affiliation: str,
        jobs: int,
    ):
        self.username = str(username)
        self.email = str(email)
        self.firstname = str(firstname)
        self.lastname = str(lastname)
        self.affiliation = str(affiliation)
        self.jobs = int(jobs)


class StatusInformation:
    def __init__(
        self,
        message: str,
        active: bool,
        jobs_in_queue: int,
        total_time_limit: int,
        uri_root: str,
        uri_signup: str,
        uri_account: str,
        uri_token: str,
        uri_problems: str,
        uri_jobs: str,
        uri_solutions: str,
    ):
        self.message = str(message)
        self.active = bool(active)
        self.jobs_in_queue = int(jobs_in_queue)
        self.total_time_limit = int(total_time_limit)
        self.uri_root = str(uri_root)
        self.uri_signup = str(uri_signup)
        self.uri_account = str(uri_account)
        self.uri_token = str(uri_token)
        self.uri_problems = str(uri_problems)
        self.uri_jobs = str(uri_jobs)
        self.uri_solutions = str(uri_solutions)


class TokenMessage:
    def __init__(self, message: str, access_token: str):
        self.message = str(message)
        self.access_token = str(access_token)


class MatrixParameters:
    def __init__(self, problem: str, nbit: int, base: int):
        self.problem = str(problem)
        self.nbit = int(nbit)
        self.base = int(base)


class QUBOMatrix:
    def __init__(self, file: str, nbit: int, base: int, qubo: list):
        self.file = str(file)
        self.nbit = int(nbit)
        self.base = int(base)
        self.qubo = qubo

    def to_json(self):
        return json.dumps(self.__dict__)


class QUBOMatrixUploadMsg:
    def __init__(self, message: str, file: str, uri_problem: str):
        self.message = message
        self.file = file
        self.uri_problem = uri_problem


class PyQUBOMatrixUploadMsg:
    def __init__(
        self,
        qubo: QUBO,
        key_mapping: Dict[int, str],
        status_code: int,
        message: str,
        file: str,
        uri_problem: str,
    ) -> None:
        self.message = message
        self.qubo = qubo
        self.uri_problem = uri_problem
        self.key_mapping = key_mapping
        self.file = file
        self.status_code = status_code

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.message=}, {self.file=}, {self.uri_problem=})"

    def decode_solution(self, solution: List[int]):
        sol: Dict[str, int] = {}
        for idx, x in enumerate(solution):
            try:
                sol[self.key_mapping[idx]] = x
            # For small Problems, we might not use all of the 32 variables.
            except KeyError:
                break
        return sol


class JobParameters:
    def __init__(self, problem: str, time_limit: str):
        self.problem = str(problem)
        self.time_limit = str(time_limit)


class PostJobSuccessMsg:
    def __init__(
        self, message: str, job: str, uri_problem: str, uri_job: str, uri_solution: str
    ):
        self.message = str(message)
        self.job = str(job)
        self.uri_problem = str(uri_problem)
        self.uri_job = str(uri_job)
        self.uri_solution = str(uri_solution)


class SolutionParameters:
    def __init__(
        self,
        time_limit: int,
        target_energy: int,
        bfactor: float,
        factor: float,
        nsolpool: int,
        ngpu: int,
        nisland_per_gpu: int,
        nisland: int,
        value_bits: int,
        arithmetic_bits: int,
    ):
        self.time_limit = int(time_limit)
        self.target_energy = int(target_energy)
        self.bfactor = float(bfactor)
        self.factor = float(factor)
        self.nsolpool = int(nsolpool)
        self.ngpu = int(ngpu)
        self.nisland_per_gpu = int(nisland_per_gpu)
        self.nisland = int(nisland)
        self.value_bits = int(value_bits)
        self.arithmetic_bits = int(arithmetic_bits)


class SolutionInformation:
    def __init__(
        self,
        terminated: bool,
        problem: str,
        job: str,
        energy: int,
        tts: float,
        solution: list,
        parameters: SolutionParameters,
        success: bool = None,
        kernel_time: float = None,
    ):
        self.terminated = bool(terminated)
        self.problem = str(problem)
        self.job = str(job)
        self.energy = int(energy)
        self.tts = float(tts)
        self.solution = list(solution)
        self.parameters = parameters
        if success is not None:
            self.success = bool(success)
        if kernel_time is not None:
            self.kernel_time = float(kernel_time)


class JobInformation:
    def __init__(
        self,
        job: str,
        problem: str,
        nbit: int,
        minval: int,
        maxval: int,
        parameters: JobParameters,
    ):
        self.job = str(job)
        self.problem = str(problem)
        self.nbit = int(nbit)
        self.minval = int(minval)
        self.maxval = int(maxval)
        self.parameters = parameters


class QUBOMatrixInformation:
    def __init__(
        self,
        file: str,
        bytes: int,
        time: datetime,
        uri_problem: str,
        verify: bool = None,
        message: str = None,
        nbit: int = None,
        nelement: int = None,
        minval: int = None,
        maxval: int = None,
        parameters: MatrixParameters = None,
    ):
        self.file = str(file)
        self.bytes = int(bytes)
        self.time = time
        self.uri_problem = str(uri_problem)
        if verify is not None:
            self.verify = bool(verify)
        if message is not None:
            self.message = str(message)
        if nbit is not None:
            self.nbit = int(nbit)
        if nelement is not None:
            self.nelement = int(nelement)
        if minval is not None:
            self.minval = int(minval)
        if maxval is not None:
            self.maxval = int(maxval)
        if parameters is not None:
            self.parameters = parameters
