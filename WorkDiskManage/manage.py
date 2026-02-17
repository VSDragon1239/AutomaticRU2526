from WorkDiskManage.App.DiskManager import DiskManager
from WorkDiskManage.settings import ProjectDirectory


def initDiskManage(project_directory_name: str):
    return DiskManager(project_directory_name)


if __name__ == '__main__':
    disks = initDiskManage(ProjectDirectory + "/TemplateData/")
    print(disks.get_storage_file())
