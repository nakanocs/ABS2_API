import json
import logging
from unittest import TestCase

from abs2 import ABS2API, ABS2Exception, models


class ABS2APITests(TestCase):
    def setUp(self) -> None:
        self._logger = logging.getLogger(__name__)
        self.api = ABS2API()
        with open("./env", "r") as f:
            user = json.load(f)
            self.user = models.UserNP(user["username"], user["password"])
        tokenMessage = self.api.retrieve_access_token(
            self.user.username, self.user.password
        )
        self.token = tokenMessage.access_token

    def tearDown(self) -> None:
        # Delete all solutions
        try:
            response = self.api.delete_all_solutions(self.token)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))
        # Delete all unexecuted jobs
        try:
            response = self.api.delete_all_unexecuted_jobs(self.token)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))
        # Delete all problems
        try:
            response = self.api.delete_all_qubo_matrices(self.token)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testStatus(self) -> None:
        try:
            status = self.api.get_status()
            assert isinstance(status, models.StatusInformation)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testRegisterUser(self) -> None:
        user = models.User(
            "<testuser>",
            "<testemail>",
            "<firstname>",
            "<lastname>",
            "<affiliation>",
        )
        try:
            response = self.api.register_user(user)
            assert response.message == "OK" and response.status_code == 201
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testUserInformation(self) -> None:
        try:
            response = self.api.retrieve_user_information(
                self.user.username, self.user.password
            )
            assert response.message == "OK" and response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testRetrieveAccessToken(self) -> None:
        try:
            tokenMessage = self.api.retrieve_access_token(
                self.user.username, self.user.password
            )
            assert isinstance(tokenMessage.access_token, str)
            assert isinstance(tokenMessage.message, str)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testGetProblemList(self) -> None:
        try:
            problems = self.api.get_all_problems(self.token)
            assert isinstance(problems, models.Result)
            assert problems.status_code == 200
            assert isinstance(problems.data, dict)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testPostMatrix(self) -> None:
        filename = "./tests/test.json"
        try:
            response = self.api.post_qubo_matrix(self.token, filename)
            assert isinstance(response, models.QUBOMatrixUploadMsg)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testGetMatrixInformation(self) -> None:
        filename = "testQUBO2.json"
        try:
            response = self.api.get_qubo_matrix_information(self.token, filename)
            assert isinstance(response, models.QUBOMatrixInformation)
            assert response.file is not None
            assert response.bytes is not None
            assert response.time is not None
            assert response.uri_problem is not None
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testDeleteMatrix(self) -> None:
        filename = "testQUBO2.json"
        try:
            response = self.api.delete_qubo_matrix(self.token, filename)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testDeleteAllMatrices(self) -> None:
        try:
            response = self.api.delete_all_qubo_matrices(self.token)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testPostJob(self) -> None:
        # TODO: create vaild QUBO Matrix with nbit > 32 for testing of the job POST method
        time_limit = 30
        problem = "testQUBO2.json"
        try:
            response = self.api.post_job(self.token, problem, time_limit)
            assert isinstance(response, models.PostJobSuccessMsg)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testGetJobInformation(self) -> None:
        job_name = "test_QUBO2_0001.json"
        try:
            response = self.api.get_job_information(self.token, job_name)
            assert isinstance(response, models.JobInformation)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testGetAllJobs(self) -> None:
        try:
            jobs = self.api.get_all_jobs(self.token)
            assert jobs.status_code == 200
            assert isinstance(jobs, models.Result)
            assert isinstance(jobs.data, dict)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testDeleteJob(self) -> None:
        job_name = "test_QUBO2_0001.json"
        try:
            response = self.api.delete_job(self.token, job_name)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testDeleteAllUnexecutedJobs(self) -> None:
        try:
            response = self.api.delete_all_unexecuted_jobs(self.token)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testGetAllSolutions(self) -> None:
        try:
            solutions = self.api.get_all_solutions(self.token)
            assert solutions.status_code == 200
            assert isinstance(solutions, models.Result)
            assert isinstance(solutions.data, dict)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testGetSolution(self) -> None:
        solution_name = "testQUBO2_0010.json"
        try:
            response = self.api.get_solution(self.token, solution_name)
            assert isinstance(response, models.SolutionInformation)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testDeleteSolution(self) -> None:
        solution_name = "testQUBO2_0001.json"
        try:
            response = self.api.delete_solution(self.token, solution_name)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testDeleteAllSolutions(self) -> None:
        try:
            response = self.api.delete_all_solutions(self.token)
            assert response.status_code == 200
        except ABS2Exception as e:
            self._logger.error(msg=str(e))

    def testPostPyQuboMatrix(self):
        qubo = {
            ("s1", "s1"): -160,
            ("s1", "s2"): 64,
            ("s2", "s2"): -96,
            ("s3", "s1"): 224,
            ("s3", "s2"): 112,
            ("s3", "s3"): -196,
            ("s4", "s1"): 32,
            ("s4", "s2"): 16,
            ("s4", "s3"): 56,
            ("s4", "s4"): -52,
        }
        try:
            response = self.api.post_pyqubo_matrix(self.token, qubo=qubo)
            self.assertEqual(response.status_code, 202)
        except ABS2Exception as e:
            self._logger.error(msg=str(e))
