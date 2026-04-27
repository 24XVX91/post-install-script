import subprocess
import os
from utils import run_cmd
class check_system:
    def __init__(self):
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
    
    def _command_exists(self, cmd):
        """检查命令是否存在"""
        try:
            self.run_cmd(cmd, shell=True, check=False, timeout=5)
            return True
        except:
            return False
    
    def _check_MLnx(self):
        """检测MLnx驱动"""
        self.is_MLnx = self._run_command("ofed_info -s")
    
    def _check_nvidia(self):
        """检测NVIDIA驱动"""
        self.is_nvidia = self._run_command("nvidia-smi -L")
    
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