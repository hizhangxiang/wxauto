import uiautomation as auto

def print_control_info(control, depth=0, file=None):
    """打印控件信息并保存到文件"""
    indent = "  " * depth
    control_type_int = control.ControlType
    control_type = auto.ControlTypeNames.get(control_type_int, str(control_type_int))
    class_name = getattr(control, 'ClassName', "N/A")
    name = control.Name if control.Name else "无名称"
    automation_id = getattr(control, 'AutomationId', "N/A")
    line = f"{indent}层级:{depth} 类型:{control_type} 类名:{class_name} 名称:{name} AutomationId:{automation_id}"
    # 如果是 EditControl，输出 ValuePattern 的值
    if control_type.lower() == "editcontrol":
        try:
            value = control.GetValuePattern().Value
            line += f" Value:{value}"
        except Exception as e:
            line += f" Value:获取失败({e})"
    line += "\n"
    if file:
        file.write(line)
    print(line, end='')

def recursive_traverse(control, max_depth=None, current_depth=0, file=None):
    print_control_info(control, current_depth, file)
    if max_depth is not None and current_depth >= max_depth:
        return
    children = control.GetChildren()
    if not children:
        return
    for child in children:
        recursive_traverse(child, max_depth, current_depth + 1, file)

# 示例用法
if __name__ == "__main__":
    # 选择要遍历的目标窗口（以微信为例，可根据需要修改）
    chrome = auto.WindowControl(searchDepth=1,ClassName='Chrome_WidgetWin_1',SubName='Google Chrome')
    if not chrome.Exists():
        chrome=auto.PaneControl(searchDepth=1,ClassName='Chrome_WidgetWin_1',SubName='Google Chrome')
    print(chrome)
    editControl_address=chrome.EditControl(name="地址和搜索栏")
    print(editControl_address)
    exit(0)
    ToolBarControl=chrome.ToolBarControl(searchDepth=5)
    print(f"ToolBarControl:{ToolBarControl}")
    editControl_address=ToolBarControl.EditControl(searchDepth=5,name='地址和搜索栏')
    print(editControl_address)
    exit()
    if chrome.Exists():
        with open("out.txt", "w", encoding="utf-8") as f:
            f.write(f"开始遍历窗口: {chrome.Name} 的所有子控件\n")
            # 递归遍历所有子控件（max_depth=None表示遍历所有层级，可设置数字限制深度）
            recursive_traverse(chrome, max_depth=None, file=f)
        print("控件信息已保存到 out.txt")
    else:
        print("未找到目标窗口，请检查窗口名称和类名是否正确")
