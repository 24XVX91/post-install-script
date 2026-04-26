from typing import List, Callable, Dict, Optional, Any
import sys
from enum import Enum


class MenuItem:
    """菜单项类，封装菜单项的所有信息"""
    
    def __init__(
        self, 
        name: str, 
        callback: Optional[Callable] = None,
        description: str = "",
        visible: bool = True,
        shortcut: Optional[str] = None
    ):
        """
        初始化菜单项
        
        Args:
            name: 菜单项名称
            callback: 选中时的回调函数
            description: 菜单项描述/帮助文本
            visible: 是否显示此菜单项（支持动态隐藏）
            shortcut: 快捷键（可选）
        """
        self.name = name
        self.callback = callback
        self.description = description
        self.visible = visible
        self.shortcut = shortcut
        self._validate()
    
    def _validate(self):
        """验证菜单项数据"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("菜单项名称必须是非空字符串")
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "callback": self.callback,
            "description": self.description,
            "visible": self.visible,
            "shortcut": self.shortcut
        }


class Menu:
    """优化的菜单选择工具类"""
    
    def __init__(
        self, 
        title: str = "",
        config: Optional[Dict] = None,
        parent: Optional['Menu'] = None
    ):
        """
        初始化菜单
        
        Args:
            title: 菜单标题
            config: 菜单配置（样式、提示词等）
            parent: 父菜单对象（用于支持返回上级）
        """
        self.title = title
        self.items: List[MenuItem] = []
        self.parent = parent
        
        # 默认配置
        self.config = {
            'separator': '=',
            'width': 50,
            'quit_key': 'q',
            'quit_message': '已退出菜单',
            'input_prompt': '请输入选项',
            'show_description': True,
            'show_shortcut': False,
            'logger': None,  # 可注入logger对象
        }
        
        # 合并用户配置
        if config:
            self.config.update(config)
    
    def add_item(
        self, 
        name: str, 
        callback: Optional[Callable] = None,
        description: str = "",
        visible: bool = True,
        shortcut: Optional[str] = None
    ) -> 'Menu':
        """
        添加菜单项
        
        Args:
            name: 菜单项名称
            callback: 选中时的回调函数
            description: 菜单项描述
            visible: 是否显示
            shortcut: 快捷键
            
        Returns:
            Menu: 返回self支持链式调用
        """
        # 检查重复
        if any(item.name == name for item in self.items):
            raise ValueError(f"菜单项 '{name}' 已存在")
        
        item = MenuItem(name, callback, description, visible, shortcut)
        self.items.append(item)
        self._log(f"Added menu item: {name}")
        return self
    
    def add_items(self, items: List[tuple]) -> 'Menu':
        """
        批量添加菜单项
        
        Args:
            items: [(name, callback), ...] 或 
                   [(name, callback, description), ...] 列表
            
        Returns:
            Menu: 返回self支持链式调用
        """
        for item in items:
            if isinstance(item, tuple):
                if len(item) == 2:
                    name, callback = item
                    self.add_item(name, callback)
                elif len(item) == 3:
                    name, callback, description = item
                    self.add_item(name, callback, description)
                elif len(item) >= 4:
                    name, callback, description, visible = item[:4]
                    self.add_item(name, callback, description, visible)
            elif isinstance(item, MenuItem):
                self.items.append(item)
        return self
    
    def set_item_visible(self, name: str, visible: bool) -> None:
        """
        动态设置菜单项的可见性
        
        Args:
            name: 菜单项名称
            visible: 是否显示
            
        示例：
            menu.set_item_visible("安装 FabricManager", gpu_is_module)
        """
        for item in self.items:
            if item.name == name:
                item.visible = visible
                self._log(f"Set item visibility: {name} -> {visible}")
                return
        self._log(f"Warning: Menu item '{name}' not found")
    
    def get_visible_items(self) -> List[MenuItem]:
        """获取所有可见的菜单项"""
        return [item for item in self.items if item.visible]
    
    def show(self) -> Optional[str]:
        """
        显示菜单并获取用户选择
        
        Returns:
            选中项的名称，或None（用户退出）
        """
        selected = self._select_item()
        return selected['name'] if selected else None
    
    def show_and_select(self) -> Optional[Dict]:
        """
        显示菜单并返回完整的菜单项对象
        
        Returns:
            选中的菜单项字典，或None
        """
        return self._select_item()
    
    def _select_item(self) -> Optional[Dict]:
        """
        核心选择逻辑（消除代码重复）
        
        Returns:
            选中的菜单项对象，或None
        """
        visible_items = self.get_visible_items()
        
        if not visible_items:
            print("❌ 菜单为空或所有项都已隐藏")
            return None
        
        while True:
            self._display(visible_items)
            choice = input(f"\n{self.config['input_prompt']} (q 退出): ").strip()
            
            if choice.lower() == self.config['quit_key']:
                print(f"✓ {self.config['quit_message']}")
                return None
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(visible_items):
                    selected = visible_items[index]
                    print(f"✓ 已选择: {selected.name}\n")
                    
                    # 执行回调函数（增强异常处理）
                    if selected.callback:
                        try:
                            self._log(f"Executing callback for: {selected.name}")
                            selected.callback()
                        except Exception as e:
                            print(f"❌ 执行 '{selected.name}' 时出错: {e}")
                            self._log(f"Error in callback: {str(e)}", level="error")
                            # 可选：继续还是返回
                            retry = input("是否继续? (y/n): ").strip().lower()
                            if retry != 'y':
                                return None
                            continue
                    
                    return selected.to_dict()
                else:
                    print(f"❌ 请输入 1-{len(visible_items)} 之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字或 'q' 退出")
    
    def _display(self, visible_items: List[MenuItem]) -> None:
        """
        显示菜单内容（支持显示描述信息）
        
        Args:
            visible_items: 可见的菜单项列表
        """
        sep = self.config['separator'] * self.config['width']
        print("\n" + sep)
        
        if self.title:
            print(f"  {self.title}")
            print(sep)
        
        # 显示菜单项
        for i, item in enumerate(visible_items, 1):
            # 基本项信息
            line = f"  {i}. {item.name}"
            
            # 添加快捷键显示（可选）
            if item.shortcut and self.config['show_shortcut']:
                line += f" [{item.shortcut}]"
            
            print(line)
            
            # 显示描述（可选）
            if item.description and self.config['show_description']:
                print(f"     └─ {item.description}")
        
        print(sep)
    
    def _log(self, message: str, level: str = "info") -> None:
        """
        记录日志（可注入自定义logger）
        
        Args:
            message: 日志信息
            level: 日志级别（info/warning/error）
        """
        if self.config['logger']:
            getattr(self.config['logger'], level, lambda x: None)(message)
        # 也可以简单地打印到stderr
        # print(f"[{level.upper()}] {message}", file=sys.stderr)


# 使用示例
if __name__ == "__main__":
    # 示例1：基础菜单（带描述）
    print("=" * 60)
    print("示例1：带描述的菜单")
    print("=" * 60)
    
    menu1 = Menu("系统后安装脚本")
    menu1.add_item("关闭ACL服务", description="禁用系统ACL，提高性能")
    menu1.add_item("安装GPU驱动", description="安装NVIDIA GPU驱动和相关工具")
    menu1.add_item("系统配置", description="其他系统优化配置")
    
    choice = menu1.show()
    print(f"您的选择: {choice}\n")
    
    # 示例2：动态菜单项（模拟GPU类型检测）
    print("=" * 60)
    print("示例2：动态菜单（根据GPU类型）")
    print("=" * 60)
    
    gpu_menu = Menu("GPU驱动安装", config={'show_description': True})
    gpu_menu.add_item("安装CUDA", description="NVIDIA CUDA工具包")
    gpu_menu.add_item("安装NVIDIA驱动", description="NVIDIA显卡驱动")
    gpu_menu.add_item(
        "安装FabricManager", 
        description="（仅模组化GPU需要）",
        visible=False  # 初始不显示
    )
    gpu_menu.add_item("安装MLNX", description="Mellanox网络工具")
    
    # 模拟GPU类型检测结果
    is_module_gpu = True  # 假设检测到是模组化GPU
    gpu_menu.set_item_visible("安装FabricManager", is_module_gpu)
    
    selected = gpu_menu.show_and_select()
    if selected:
        print(f"选中项信息: {selected}\n")
    
    # 示例3：自定义样式和提示
    print("=" * 60)
    print("示例3：自定义样式菜单")
    print("=" * 60)
    
    custom_config = {
        'separator': '-',
        'width': 60,
        'quit_key': 'q',
        'quit_message': '返回上级菜单',
        'input_prompt': '请选择',
        'show_description': True,
    }
    
    menu3 = Menu("自定义安装驱动", config=custom_config)
    menu3.add_item("从整合包安装", description="使用预配置的整合包（推荐）")
    menu3.add_item("自定义组件安装", description="手动选择要安装的组件")
    menu3.add_item("从公网下载", description="从官方网站下载最新驱动")
    
    menu3.show()