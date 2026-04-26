import re
import subprocess
import requests

# ===================== 配置 =====================
UBUNTU_VERSION = "2204"  # 20.04=2004，22.04=2204
# ==================================================

def get_driver_version():
    """获取本机 NVIDIA 驱动版本"""
    try:
        out = subprocess.check_output(["nvidia-smi"], encoding="utf-8")
        match = re.search(r"Driver Version:\s*([\d]+\.[\d]+\.[\d]+)", out)
        if match:
            return match.group(1)
    except Exception:
        raise Exception("获取驱动版本失败，请安装 NVIDIA 驱动")
    raise Exception("无法识别驱动版本")

def find_correct_package(driver_ver: str, ubuntu_ver: str):
    """
    终极匹配：
    只匹配 官方运行版 amd64 deb 包
    自动忽略所有 dev/dbg/src/static 等杂包
    无论未来怎么改名都有效
    """
    base_url = f"https://developer.download.nvidia.com/compute/cuda/repos/ubuntu{ubuntu_ver}/x86_64/"
    resp = requests.get(base_url, timeout=15)
    resp.raise_for_status()

    # ===================== 宇宙最强正则 =====================
    pattern = re.compile(
        rf'href="(nvidia-fabricmanager(?:-\d+)?_{re.escape(driver_ver)}[^"]*?_amd64.deb)"'
    )

    packages = pattern.findall(resp.text)
    if not packages:
        raise Exception(f"未找到 版本 {driver_ver} 对应的官方运行包")

    # 去重取第一个
    pkg = sorted(set(packages))[0]
    return base_url + pkg, pkg

def download(url: str, filename: str):
    print(f"下载中：{filename}")
    with requests.get(url, stream=True, timeout=20) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(1024*1024):
                f.write(chunk)
    print(f"下载完成：{filename}")

if __name__ == "__main__":
    try:
        driver_ver = get_driver_version()
        print(f"[+] 驱动版本：{driver_ver}")

        url, filename = find_correct_package(driver_ver, UBUNTU_VERSION)
        print(f"[+] 找到正确包：{url}")

        download(url, filename)
        print("\n✅ 成功！")
        
    except Exception as e:
        print(f"\n❌ 错误：{e}")