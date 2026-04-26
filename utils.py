

def run_cmd(self, cmd, shell=False, check=True, timeout=30, retry=1):

    for attempt in range(retry):
        try:
            self.logger.info(f"[{attempt+1}/{retry}] Executing: {cmd}")
            result = subprocess.run(
                cmd, 
                shell=shell, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                check=check,
                timeout=timeout  # 添加超时
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Command timed out: {cmd}")
            if attempt < retry - 1:
                continue
            raise
        except subprocess.CalledProcessError as e:
            if attempt < retry - 1:
                self.logger.warning(f"Attempt {attempt+1} failed, retrying...")
                continue
            raise



