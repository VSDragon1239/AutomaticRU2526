from WorkJSONFiles.App.JSONDataManager import JSONDataManager
from WorkJSONFiles.TemplateData.TestData import test_user_data, test_profile_data, test_user_data_only_last_name
from WorkJSONFiles.api import apiFilesService
from WorkJSONFiles.settings import FullTestDirectory


def TestingJsonFiles():
    print('Начало теста файла')
    TestDirJSONDataFiles = apiFilesService(FullTestDirectory)
    TestDirJSONDataFiles.read_file("UserFile")

    TestDirJSONDataFiles.delete_file("ProfileFile")
    TestDirJSONDataFiles.delete_file("UserFile")

    TestDirJSONDataFiles.write_data("UserFile", test_user_data())
    TestDirJSONDataFiles.write_data("UserFile", test_user_data_only_last_name())
    TestDirJSONDataFiles.write_data("ProfileFile", test_profile_data())


if __name__ == '__main__':
    print('TestingJsonFiles Is manage.py')
    TestingJsonFiles()

