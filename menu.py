import sys

class AutoInstaller:
    def __init__(self):
        # 初始化一个有序的字典来存储菜单项
        self.menu_items = {}
        
        # 【核心】：在这里统一注册功能
        # 格式: 选项key, 菜单显示文本, 对应的执行函数
        self.register_action('1', '选择执行系统初始化配置', self.system_initialization)
        self.register_action('2', '安装NVIDIA应用软件', self.install_nvidia_suite)
        self.register_action('3', '其他功能', lambda: print("其他功能暂未实现"))
        
        # 增量开发举例：如果明天你要加一个安装Docker的功能，只需加下面这一行，并写好函数即可
        # self.register_action('4', '安装 Docker 环境', self.install_docker)

        self.register_action('q', '退出脚本', self.exit_script)

    def register_action(self, key, description, func):
        """通用的功能注册方法"""
        self.menu_items[key] = {
            'desc': description,
            'func': func
        }

    def exit_script(self):
        print("退出脚本。")
        sys.exit(0)

    def show_menu(self):
        while True:
            print("\n" + "="*30)
            print(" 自动化安装脚本功能菜单 ")
            print("="*30)
            
            # 动态生成菜单UI，不用再手动 print 1234 了
            for key, item in self.menu_items.items():
                print(f"{key}. {item['desc']}")
            
            choice = input("请输入选项: ").strip().lower()
            
            # 动态查找并执行
            action = self.menu_items.get(choice)
            if action:
                action['func']() # 执行函数
            else:
                print("无效的输入，请重新选择。")