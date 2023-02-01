from unittest import TestCase

from abs2 import ABS2Exception, models, rest_adapter


class AdapterTests(TestCase):
    @staticmethod
    def testAdapter():
        root = "qubosolver.cs.hiroshima-u.ac.jp"
        api = rest_adapter.RestAdapter(root)
        result = api.get("")
        status = models.StatusInformation(**result.data)
        print(status)

    def testIncorrectEndpoint(self):
        root = "qubosolver.cs.hiroshima-u.ac.jp"
        api = rest_adapter.RestAdapter(root)
        with self.assertRaises(ABS2Exception):
            response = api.get("badendpoint")
