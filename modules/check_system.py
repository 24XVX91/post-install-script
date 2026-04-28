import os

from sos.report.plugins import nvidia

import utils.run_cmd as run_cmd
class check_system(run_cmd.BaseManager):
    def __init__(self):
        super().__init__()
        self.is_MLnx = False
        self.is_nvidia = False
        self.is_cuda = False
        self.is_NVsw = False
        self.is_FMger = None

        # 执行检测
        self._check_MLnx()
        self._check_nvidia()
        self._check_cuda()
        self._check_NVsw()
        self._check_FMger()

    
    def _run_command(self, cmd):
        """检查命令是否存在"""
        try:
            return self.run_cmd(cmd, shell=True, check=True, timeout=5)

        except:
            return False

    
    def _check_MLnx(self):
        """检测MLnx驱动"""
        self.is_MLnx = self._run_command("ofed_info -n")
    
    def _check_nvidia(self):
        """检测NVIDIA驱动"""
        self.is_nvidia = self._run_command(" nvidia-smi --version")
    
    def _check_cuda(self):
        """检测CUDA"""
        self.is_cuda = self._run_command("/usr/local/cuda/bin/nvcc -V")
    
    def _check_NVsw(self):
        """检测NVswitch"""
        self.is_NVsw = os.path.exists("/dev/nvidia-NVswitch")
    def _check_FMger(self):
        """检测nvidia-fabricmanager（仅当NVswitch存在时检测）"""
        if self.is_NVsw:
            self.is_FMger = self._run_command("nv-fabricmanager --version")
        else:
            self.is_FMger = None