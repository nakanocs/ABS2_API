import logging
import string
from random import choices
from typing import Optional

from .models import *
from .rest_adapter import RestAdapter


class ABS2API:
    def __init__(
        self,
        hostname: str = "qubosolver.cs.hiroshima-u.ac.jp",
        api_key: str = "",
        ver: str = "v1",
        ssl_verify: bool = True,
        logger: logging.Logger = None,
    ):
        self._rest_adapter = RestAdapter(hostname, api_key, ver, ssl_verify, logger)

    def get_status(self) -> StatusInformation:
        """
        Check if the QUBO solver is working. The web API returns StatusInformation.
        :return: StatusInformation, return codes: 200 (OK, QUBO solver working),
                                                  503 (SERVICE_UNAVAILABLE, QUBO solver is not working)
        """
        result = self._rest_adapter.get(endpoint="")
        return StatusInformation(**result.data)

    def register_user(self, user: User) -> Result:
        """
        Register a user with the QUBO solver. A user needs to be registered with the solver to retrieve an access token.
        A User object is required containing the username, email, firstname, lastname and affiliation.
        An email containing the generated password belonging to the newly registered user will be sent to the
        provided email address.
        :param user: user Object
        :return: Result, return codes: 201 (CREATED, user account creation succeeded),
                                       400 (BAD_REQUEST, malformed parameters),
                                       409 (CONFLICT, username and/or email already registered
        """
        return self._rest_adapter.post("signup", data=user.__dict__)

    def retrieve_user_information(self, username: str, password: str) -> Result:
        """
        Retrieve information about a user that has been created previously.
        :param username: the username of the user, as it was provided when registering the user
        :param password: the password of the user, as it was sent to the user's email after registration
                         or a custom password set through the change_password() method
        :return: Result, return codes: 200 (OK, user information retrieved correctly),
                                       400 (BAD_REQUEST, malformed parameters)
                                       401 (UNAUTHORIZED, wrong password)
                                       404 (NOT_FOUND, no user account associated with the username)
        """
        return self._rest_adapter.post(
            "account", data={"username": username, "password": password}
        )

    def retrieve_access_token(self, username: str, password: str) -> TokenMessage:
        """
        To do most things related to the QUBO solver an access token is required.
        It can be retrieved through this method.
        :param username: the username of the user, as it was provided when registering the user
        :param password: the password of the user, as it was sent to the user's email after registration
                         or a custom password set through the change_password() method
        :return: TokenMessage, status codes: 200 (OK, access token retrieved),
                                             400 (BAD_REQUEST, malformed parameters)
                                             401 (UNAUTHORIZED, wrong password)
                                             404 (NOT_FOUND, no user associated with the username)
        """
        result = self._rest_adapter.post(
            "token", data={"username": username, "password": password}
        )
        return TokenMessage(**result.data)

    def retrieve_new_password(self, username: str, email: str) -> Result:
        """
        Retrieve a new password should the old password be lost or forgotten.
        :param username: the username of the user, as it was provided when registering the user
        :param email: the email of the user, as it was provided when registering the user
        :return: Result, return codes: 200 (OK, new password is emailed),
                                       401 (UNAUTHORIZED, email is wrong),
                                       404 (NOT_FOUND, no user associated with the username)
        """
        return self._rest_adapter.post(
            "account", data={"username": username, "email": email}
        )

    def retrieve_new_username(self, email: str) -> Result:
        """
        Retrieve a new username should the old username be lost of forgotten
        :param email: the email of the user, as it was provided when registering the user
        :return: Result, status codes: 200 (OK, retrieve username),
                                       400 (BAD_REQUEST, malformed parameters),
                                       404 (NOT_FOUND, no user account associated with email)
        """
        return self._rest_adapter.post("account", data={"email": email})

    def change_password(
        self, username: str, password: str, new_password: str
    ) -> Result:
        """
        The password can be updated if desired.
        :param: username: the username of the user, as it was provided when registering the user
        :param: password: the current password of the user
        :param: new_password: the new password of the user
        :return: Result, status codes: 200 (OK, password changed successfully),
                                       400 (BAD_REQUEST, malformed parameters or the new password
                                            is violating the conditions for passwords),
                                       401 (UNAUTHORIZED, wrong password),
                                       404 (NOT_FOUND, no user associated with the username)
        """
        return self._rest_adapter.put(
            "account",
            data={
                "username": username,
                "password": password,
                "newpassword": new_password,
            },
        )

    def delete_user_account(self, token: str) -> Result:
        """
        The user account can be deleted if desired.
        :param: token: The bearer token, which can be retrieved through the retrieve_access_token() method
        :return: Result, status codes: 200 (OK, deletion of user account is completed),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        return self._rest_adapter.delete(
            "account", additional_headers={"Authorization": f"Bearer {token}"}
        )

    def post_qubo_matrix(self, token: str, filename: str) -> QUBOMatrixUploadMsg:
        """
        Loads a QUBO Matrix in JSON format from a file to be directly uploaded for processing by the QUBO solver.
        The minimum number for nbit is 32.
        The content of the file needs the following format:
            {
                "file": "testQUBO2.json",
                "nbit": 32,
                "base": 0,
                "qubo": [
                    [1, 0, 1],
                    [0, 1, -1]
                ]
            }
        Once the QUBO matrix file is uploaded, the web API starts the verification process of the file.
        The verification time scales with the size of the file.
        The verification process checks if the uploaded file follows the previously mentioned JSON format
        and converts it to a by the QUBO solver handleable file format.
        Jobs for solving the QUBO problem can be submitted after the verification is completed.
        :param token: The bearer token of the registered user
        :param filename: The file name of the file that is to be uploaded
        :return: QUBOMatrixUploadMsg, status codes: 202 (ACCEPTED, QUBO matrix uploaded and verification started),
                                                    400 (BAD_REQUEST, malformed parameters),
                                                    401 (UNAUTHORIZED, wrong access token),
                                                    415 (UNSUPPORTED_MEDIA_TYPE, file is not JSON data format)
        """
        with open(filename, "r") as f:
            matrix = json.load(f)
        result = self._rest_adapter.post(
            "problems",
            additional_headers={"Authorization": f"Bearer {token}"},
            data=matrix,
        )
        return QUBOMatrixUploadMsg(**result.data)

    def post_pyqubo_matrix(
        self, token: str, qubo: QUBO, file: Optional[str] = None
    ) -> PyQUBOMatrixUploadMsg:
        """Loads a QUBO Matrix in dict format from a file to be directly uploaded for processing by the QUBO solver.

        Once the QUBO matrix file is uploaded, the web API starts the verification process of the matrix.
        The verification time scales with the size of the file.
        The verification process checks if the uploaded file follows the previously mentioned JSON format
        and converts it to a by the QUBO solver handleable file format.
        Jobs for solving the QUBO problem can be submitted after the verification is completed.
        The return value can be used to decode the solution once it is solved.
        :param token: The bearer token of the registered user
        :param filename: The file name of the file that is to be uploaded
        :return: PyQUBOMatrixUploadMsg, status codes: 202 (ACCEPTED, QUBO matrix uploaded and verification started),
                                                    400 (BAD_REQUEST, malformed parameters),
                                                    401 (UNAUTHORIZED, wrong access token),
                                                    415 (UNSUPPORTED_MEDIA_TYPE, file is not JSON data format)"""
        # Prepare filename
        if file is None:
            file = "".join(choices(string.ascii_lowercase, k=10)) + ".json"
        # Prepare problem
        keys = {k[0] for k in qubo.keys()} | {k[1] for k in qubo.keys()}
        key_index_mapping: Dict[str, int] = {name: idx for idx, name in enumerate(keys)}
        qubo_matrix = [
            [key_index_mapping[n1], key_index_mapping[n2], int(v)]
            for (n1, n2), v in qubo.items()
        ]
        nbit = max(32, len(keys))
        base = 0

        matrix = {"file": file, "nbit": nbit, "base": base, "qubo": qubo_matrix}

        result = self._rest_adapter.post(
            "problems",
            additional_headers={"Authorization": f"Bearer {token}"},
            data=matrix,
        )

        return PyQUBOMatrixUploadMsg(
            qubo=qubo,
            key_mapping={v: k for k, v in key_index_mapping.items()},
            status_code=result.status_code,
            **result.data,
        )

    def get_qubo_matrix_information(
        self, token: str, filename: str
    ) -> QUBOMatrixInformation:
        """
        Get information on an uploaded Matrix file. Based on the verification success / failure, different information
        will be retrieved.
        :param token: The bearer token of the user
        :param filename: the filename of the QUBO matrix
                        (Note: This refers to the filename given within the JSON structure)
        :return: QUBOMatrixInformation, status codes: 200 (OK, information on the QUBO matrix received),
                                                      401 (UNAUTHORIZED, wrong access token),
                                                      404 (NOT_FOUND, file not found)
        """
        result = self._rest_adapter.get(
            f"problems/{filename}",
            additional_headers={"Authorization": f"Bearer {token}"},
        )
        return QUBOMatrixInformation(**result.data)

    def get_all_problems(self, token: str) -> Result:
        """
        Get a full list of uploaded QUBO matrix files.
        :param token: The bearer token of the user
        :return: Result, status codes: 200 (OK, a list of all files was obtained),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        result = self._rest_adapter.get(
            "problems", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def delete_qubo_matrix(self, token: str, name: str) -> Result:
        """
        Delete a QUBO matrix by providing the filename.
        The deletion may be incomplete if the file is deleted during the verification process.
        :param token: the bearer token of the user
        :param name: the filename of the QUBO matrix file that should be deleted
        :return: Result, status codes: 200 (OK, problem is deleted),
                                       401 (UNAUTHORIZED, wrong access token),
                                       404 (NOT_FOUND, file not found)
        """
        result = self._rest_adapter.delete(
            f"problems/{name}", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def delete_all_qubo_matrices(self, token: str) -> Result:
        """
        Delete all QUBO matrices. The deletion may be incomplete if a file is deleted during its verification process.
        :param token: the bearer token of the user
        :return: Result, status codes: 200 (OK, all problems deleted),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        result = self._rest_adapter.delete(
            "problems", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def post_job(self, token: str, problem: str, time_limit: int) -> PostJobSuccessMsg:
        """
        Posts a job to the web API. Posting a job is possible for problems that complete verification.
        Notes: The name of a job is based on the name of the file of the problem.
               Usually it is the name of the file with four digits appended to the end.
               Job files are passed in the order of posting, and the QUBO solver works for jobs in turn.
               When a job is assigned to the QUBO solver,
               the job file on the web API will be moved from the directory "jobs" to the directory "solutions"
               Intermediate and the final solutions obtained by the QUBO solver are overwritten in the solution file.
               The QUBO solver updates the solution file when it finds a better solution.
               When the QUBO solver terminates, the solution file stores the best solution obtained by it
        :param token: the bearer token of the user
        :param problem: the filename of the QUBO matrix in the directory "problems"
        :param time_limit: a time limit for the solver (minutes?)
        :return: PostJobSuccessMsg, status codes: 102 (PROCESSING, posting a job failed because
                                                        verification is in progress),
                                                  202 (ACCEPTED, posting job succeeded),
                                                  400 (BAD_REQUEST, malformed parameters),
                                                  401 (UNAUTHORIZED, wrong access token),
                                                  404 (NOT_FOUND, no QUBO matrix found or verification failed)
        """
        result = self._rest_adapter.post(
            "jobs",
            additional_headers={"Authorization": f"Bearer {token}"},
            data={"problem": problem, "time_limit": time_limit},
        )
        return PostJobSuccessMsg(**result.data)

    def get_job_information(self, token: str, job_name: str) -> JobInformation:
        """
        Get information about an unexecuted job.
        :param token: the bearer token of the user
        :param job_name: the file name of the job
        :return: JobInformation, status codes: 200 (OK, retrieved information about the specified job),
                                               401 (UNAUTHORIZED, wrong access token),
                                               404 (NOT_FOUND, job file not found)
        """
        result = self._rest_adapter.get(
            f"jobs/{job_name}", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return JobInformation(**result.data)

    def get_all_jobs(self, token: str) -> Result:
        """
        Get a list of all unexecuted jobs. If a job is posted when the QUBO solver is waiting for a new job,
        it is executed immediately. The posted job therefore will not be shown in the list.
        :param token: the bearer token of the user
        :return: Result, status codes: 200 (OK, retrieved a list of all jobs),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        result = self._rest_adapter.get(
            "jobs", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def delete_job(self, token: str, job_name: str) -> Result:
        """
        Deletes a job by filename.
        :param token: the bearer token of the user
        :param job_name: the filename of the job
        :return: Result, status codes: 200 (OK, job file deleted),
                                       401 (UNAUTHORIZED, wrong access token)
                                       404 (NOT_FOUND, file not found)
        """
        result = self._rest_adapter.delete(
            f"jobs/{job_name}", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def delete_all_unexecuted_jobs(self, token: str) -> Result:
        """
        Deletes all unexecuted jobs.
        :param token: the bearer token of the user
        :return: Result, status codes: 200 (OK, all jobs deleted),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        result = self._rest_adapter.delete(
            "jobs", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def get_all_solutions(self, token: str) -> Result:
        """
        Retrieves a list of all solution files.
        :param token: the bearer token of the user
        :return: Result, status codes: 200 (OK, retrieved a list of all solutions),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        result = self._rest_adapter.get(
            "solutions", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result

    def get_solution(self, token: str, solution_name: str) -> SolutionInformation:
        """
        Retrieve a solution by its solution file name.
        Notes:  The value of key "terminated" is true if the QUBO solver is terminated.
                The value of key "success" is false if the QUBO solver is abnormally terminated
        :param token: the bearer token of the user
        :param solution_name: the file name of the solution file
        :return: SolutionInformation, status codes: 200 (OK, the solution vector, etc. obtained correctly),
                                                    401 (UNAUTHORIZED, wrong access token),
                                                    404 (NOT_FOUND, file not found)
        """
        result = self._rest_adapter.get(
            f"solutions/{solution_name}",
            additional_headers={"Authorization": f"Bearer {token}"},
        )
        return SolutionInformation(**result.data)

    def delete_solution(self, token: str, solution_name: str) -> Result:
        """
        Deletes a solution file by it solution file name.
        Notes:  Trying to delete a file the QUBO solver is currently working on, may result in incomplete deletion
        :param token: the bearer token of the user
        :param solution_name: the file name of the solution file
        :return: Result, status codes: 200 (OK, solution file deleted),
                                       401 (UNAUTHORIZED, wrong access token),
                                       404 (NOT_FOUDN, solution file not found)
        """
        result = self._rest_adapter.delete(
            f"solutions/{solution_name}",
            additional_headers={"Authorization": f"Bearer {token}"},
        )
        return result

    def delete_all_solutions(self, token: str) -> Result:
        """
        Deletes all solution files.
        Notes:  Trying to delete a file the QUBO solver is currently working on, may result in incomplete deletion
        :param token: the bearer token of the user
        :return: Result, status codes: 200 (OK, all solution files deleted),
                                       401 (UNAUTHORIZED, wrong access token)
        """
        result = self._rest_adapter.delete(
            "solutions", additional_headers={"Authorization": f"Bearer {token}"}
        )
        return result
