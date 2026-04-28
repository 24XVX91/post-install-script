from modules.check_system import check_system
import utils.run_cmd as run_cmd
import menu

"""安装选择器"""
class InstallSelector():
    """根据系统检测结果选择安装驱动"""

    def __init__(self):
        self.checker = check_system()

    def get_status(self):
        """返回系统检测状态，供菜单使用"""
        return {
            'mlnx_missing': not  self.checker.is_MLnx,
            'nvidia_missing': not self.checker.is_nvidia or not self.checker.is_cuda,
            'fabricmanager_missing':  self.checker.is_FMger is False
        }
    def get_checker(self):

        '''MLNX驱动格式'''
        MLNX_version = self.checker.is_MLnx
        if not MLNX_version:
            MLNX_version = "未检测到MLNX驱动"

        '''英伟达驱动格式处理'''
        nvidia_version = self.checker.is_nvidia
        if not nvidia_version:
            nvidia_version = "未检测到nvidia驱动"
        else:
            for line in nvidia_version.splitlines():
                if "DRIVER version" in line:
                    # 按冒号分割 → 取右边 → 去空格
                    nvidia_version = line.split(":", 1)[1].strip()
                    break

        """cuda驱动格式处理"""
        cuda_version = self.checker.is_cuda
        if not cuda_version:
            cuda_version = "未检测到cuda驱动"
        else:
            for line in cuda_version.splitlines():
                if "Cuda compilation tools" in line:
                    # 提取 V 后面的版本号 V12.8.61
                    parts = line.split()
                    for p in parts:
                        if p.startswith("V") and p[1:].replace(".", "").isdigit():
                            cuda_version = p
                            break
                    break

        """fabricmanager驱动格式处理"""
        fmger_version = self.checker.is_FMger
        if fmger_version is None:
            fmger_version = "不支持NVSwitch,不需要fabricmanager"
        elif not fmger_version:
            fmger_version = "未检测到fabricmanager驱动"
        else:
            for line in fmger_version.splitlines():
                if "Fabric Manager version" in line:
                    # 按冒号分割，取后面的版本号
                    fmger_version = line.split(":")[-1].strip()
                    break
        return {
            'MLNX': MLNX_version,
            'nvidia': nvidia_version,
            'cuda': cuda_version,
            'fabricmanager': fmger_version
        }


insta = InstallSelector()
print(insta.get_checker())