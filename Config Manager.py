import json
from scripts import LangConfigMgr
import os


def clear():
    # 如果是Windows系统 (If it is a Windows system)
    if os.name == 'nt':
        os.system('cls')
    else:
        # 对于mac和linux（os.name是'posix'） (For mac and linux (os.name is 'posix'))
        os.system('clear')


while True:
    clear()  # 在循环开始时清屏 (Clear the screen at the beginning of the loop)
    mgr_choice = int(input(
        "What do you want to do?\n1. Configure language\n2. Configure other settings\n3. Exit\nEnter your choice (1~3): "))

    if mgr_choice == 1:
        clear()
        LangConfigMgr.lang_manager()
        input("Press Any key to continue...")
        clear()  # 在语言配置后清屏 (Clear the screen after language configuration)
    elif mgr_choice == 2:
        clear()

        # 读配置 (Read configuration)
        with open(os.path.join("Configs", "Config.json"), 'r', encoding="utf-8") as config_file:
            config_data = json.load(config_file)

        # 读注释 (Read comments)
        with open(os.path.join("Configs", "Comments.json"), 'r', encoding="utf-8") as comments_file:
            comments_data = json.load(comments_file)

        # 打印键值对和注释 (Print key-value pairs and comments)
        settings_list = list(config_data.items())
        for index, (key, value) in enumerate(settings_list, start=1):
            print(f"{index}. {key}: {value}")
            print(comments_data[key])

        setting_index = int(input("Enter the index of the setting you want to modify: "))

        # 检测输入是否合法 (Check if input is valid)
        if 1 <= setting_index <= len(settings_list):
            # Adjust the index to 0-based for list access
            adjusted_index = setting_index - 1
            # 获取键 (Get key)
            setting_key = settings_list[adjusted_index][0]
            # 获取当前值和类型 (Get current value and type)
            current_value = config_data[setting_key]
            value_type = type(current_value).__name__

            new_value = input(f"Enter the new value for '{setting_key}' (current type is {value_type}): ")

            # 转换类型 (Convert type)
            if value_type == 'int':
                new_value = int(new_value)
            elif value_type == 'float':
                new_value = float(new_value)
            elif value_type == 'bool':
                new_value = new_value.lower() in ['true', '1', 't', 'y', 'yes']

            # 写配置 (Write configuration)
            config_data[setting_key] = new_value

            # 写配置文件 (Write to the configuration file)
            with open(os.path.join("Configs", "Config.json"), 'w') as config_file:
                json.dump(config_data, config_file, indent=4)
            print(f"Setting '{setting_key}' has been updated to '{new_value}'.")
            input("Press Any key to continue...")
            clear()  # 在配置更新后清屏 (Clear the screen after configuration update)
        else:
            print("Invalid index. No changes made.")
            clear()  # 在无效输入后清屏 (Clear the screen after invalid input)
    elif mgr_choice == 3:
        break
