import unittest

from WorkJSONFiles.api import apiFilesService
from WorkProjectManager.App.StructureManager import StructureManager
from WorkProjectManager.settings import FullTestDirectory

MainIFS = apiFilesService(FullTestDirectory)


def get_test_data_project_1():
    return ["TestName1", "TestDescription1"]


def get_test_data_project_2():
    return ["TestNameProject1", "TestTypeProject1", "TestDescriptionProject1"]


class TestDataManager(unittest.TestCase):
    ClassTest = StructureManager(MainIFS)
    ClassTest.load_all_data()

    def test_global_projects_list_data(self):
        self.assertEqual(type(self.ClassTest.globalProjectsList), list)  # Тестирование правильного типа данных
        self.assertEqual(self.ClassTest.globalProjectsList, [])  # Ничего лишнего не прилетело при первом включении

    def test_new_global_project_list_data(self):
        self.ClassTest.new_global_project_data(get_test_data_project_1()[0], get_test_data_project_1()[1])
        self.assertEqual(self.ClassTest.globalProjectsList,
                         [{
                             'GlobalProjectID': "1",
                             'GlobalProjectName': get_test_data_project_1()[0],
                             'GlobalProjectDescription': get_test_data_project_1()[1],
                             'GlobalProjectProjectsData': []
                         }])
        self.assertEqual(self.ClassTest.get_last_global_project_id(), 1)

    def test_edit_global_project_data(self):
        self.test_new_global_project_list_data()

        testName = "TestEditName1"
        testDesc = "TestEditDesc1"
        self.ClassTest.edit_global_project_data(self.ClassTest.get_last_global_project_id(), "GlobalProjectName",
                                                f"{testName}")
        self.ClassTest.edit_global_project_data(self.ClassTest.get_last_global_project_id(), "GlobalProjectDescription",
                                                f"{testDesc}")
        self.assertEqual(self.ClassTest.globalProjectsList,
                         [{
                             'GlobalProjectID': '1',
                             'GlobalProjectName': f"{testName}",
                             'GlobalProjectDescription': f"{testDesc}",
                             'GlobalProjectProjectsData': []
                         }])
        with self.assertRaises(ValueError):
            self.ClassTest.edit_global_project_data(self.ClassTest.get_last_global_project_id(),
                                                    "GlobalProjectID", "")
        with self.assertRaises(ValueError):
            self.ClassTest.edit_global_project_data(self.ClassTest.get_last_global_project_id(),
                                                    "GlobalProjectProjectsData", "")

    def test_global_project_projects_list_data(self):
        self.test_new_global_project_list_data()
        self.ClassTest.load_projects_data(self.ClassTest.get_last_global_project_id())

        self.assertEqual(type(self.ClassTest.globalProjectProjectsList), list)
        self.assertEqual(self.ClassTest.globalProjectProjectsList, [])

        self.assertEqual(self.ClassTest.get_last_project_id(), 0)

        self.ClassTest.new_project_data(get_test_data_project_2()[0], get_test_data_project_2()[1],
                                        get_test_data_project_2()[2])
        self.assertEqual(self.ClassTest.globalProjectProjectsList,
                         [{
                             'ProjectID': '1',
                             'ProjectName': f"{get_test_data_project_2()[0]}",
                             'ProjectType': f"{get_test_data_project_2()[1]}",
                             'ProjectDescription': f"{get_test_data_project_2()[2]}",
                             'ProjectData': []
                         }])
        self.assertEqual(self.ClassTest.globalProjectsList,
                         [{
                             'GlobalProjectID': "1",
                             'GlobalProjectName': get_test_data_project_1()[0],
                             'GlobalProjectDescription': get_test_data_project_1()[1],
                             'GlobalProjectProjectsData': [
                                 {
                                     'ProjectID': '1',
                                     'ProjectName': f"{get_test_data_project_2()[0]}",
                                     'ProjectType': f"{get_test_data_project_2()[1]}",
                                     'ProjectDescription': f"{get_test_data_project_2()[2]}",
                                     'ProjectData': []
                                 }
                             ]
                         }])

    def test_edit_global_project_projects_list_data(self):
        self.test_global_project_projects_list_data()
        testName = "TestEditProjectName1"
        testType = "TestEditProjectType1"
        testDesc = "TestEditProjectDesc1"

        self.ClassTest.edit_project_data(self.ClassTest.get_last_project_id(), "ProjectName", f"{testName}")
        self.ClassTest.edit_project_data(self.ClassTest.get_last_project_id(), "ProjectType", f"{testType}")
        self.ClassTest.edit_project_data(self.ClassTest.get_last_project_id(), "ProjectDescription", f"{testDesc}")
        self.assertEqual(self.ClassTest.globalProjectProjectsList,
                         [{
                             'ProjectID': '1',
                             'ProjectName': f"{testName}",
                             'ProjectType': f"{testType}",
                             'ProjectDescription': f"{testDesc}",
                             'ProjectData': []
                         }])
        with self.assertRaises(ValueError):
            self.ClassTest.edit_project_data(self.ClassTest.get_last_project_id(),
                                             "ProjectID", "")
        with self.assertRaises(ValueError):
            self.ClassTest.edit_project_data(self.ClassTest.get_last_project_id(),
                                             "ProjectData", "")

    def test_remove_global_project_projects_list_data(self):
        self.test_global_project_projects_list_data()
        self.ClassTest.delete_project_data(self.ClassTest.get_last_project_id())
        self.assertEqual(self.ClassTest.globalProjectProjectsList, [])

    def test_remove_global_project_list_data(self):
        self.test_new_global_project_list_data()
        self.ClassTest.delete_global_project_data(self.ClassTest.get_last_global_project_id())
        self.assertEqual(self.ClassTest.globalProjectsList, [])


if __name__ == '__main__':
    unittest.main()
