import unittest

from WorkJSONFiles.api import apiFilesService
from WorkProjectManager.App.StructureManager import StructureManager
from WorkProjectManager.settings import FullTestDirectory

MainIFS = apiFilesService(FullTestDirectory)


def get_test_data_application_1():
    return ["TestApplicationName1", "TestApplicationType1", "TestApplicationInstallerPath1",
            "TestApplicationDescription1"]


def get_test_data_application_2():
    return ["TestEditApplicationName1", "TestEditApplicationType1", "TestEditApplicationInstallerPath1",
            "TestEditApplicationDescription1"]


class TestDataManager(unittest.TestCase):
    ClassTest = StructureManager(MainIFS)
    ClassTest.load_all_data()

    def test_applications_list_data(self):
        self.assertEqual(type(self.ClassTest.applicationsList), list)  # Тестирование правильного типа данных
        self.assertEqual(self.ClassTest.applicationsList, [])  # Ничего лишнего не прилетело при первом включении

    def test_new_application_list_data(self):
        self.ClassTest.new_application_data(get_test_data_application_1()[0], get_test_data_application_1()[1], get_test_data_application_1()[2], get_test_data_application_1()[3])
        self.assertEqual(self.ClassTest.applicationsList,
                         [{
                             'ApplicationID': "1",
                             'ApplicationName': get_test_data_application_1()[0],
                             'ApplicationType': get_test_data_application_1()[1],
                             "ApplicationInstallerPath": get_test_data_application_1()[2],
                             'ApplicationDescription': get_test_data_application_1()[3]
                         }])
        self.assertEqual(self.ClassTest.get_last_application_id(), 1)

    def test_edit_application_data(self):
        self.test_new_application_list_data()

        self.ClassTest.edit_application_data(self.ClassTest.get_last_application_id(), "ApplicationName",
                                             f"{get_test_data_application_2()[0]}")
        self.ClassTest.edit_application_data(self.ClassTest.get_last_application_id(), "ApplicationType",
                                             f"{get_test_data_application_2()[1]}")
        self.ClassTest.edit_application_data(self.ClassTest.get_last_application_id(), "ApplicationInstallerPath",
                                             f"{get_test_data_application_2()[2]}")
        self.ClassTest.edit_application_data(self.ClassTest.get_last_application_id(), "ApplicationDescription",
                                             f"{get_test_data_application_2()[3]}")
        self.assertEqual(self.ClassTest.applicationsList,
                         [{
                             'ApplicationID': "1",
                             'ApplicationName': get_test_data_application_2()[0],
                             'ApplicationType': get_test_data_application_2()[1],
                             "ApplicationInstallerPath": get_test_data_application_2()[2],
                             'ApplicationDescription': get_test_data_application_2()[3]
                         }])
        with self.assertRaises(ValueError):
            self.ClassTest.edit_application_data(self.ClassTest.get_last_application_id(),
                                                 "ApplicationID", "")

    def test_remove_global_project_projects_list_data(self):
        self.test_new_application_list_data()
        self.ClassTest.delete_application_data(self.ClassTest.get_last_application_id())
        self.assertEqual(self.ClassTest.applicationsList, [])


if __name__ == '__main__':
    unittest.main()
