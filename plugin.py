from typing import List, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    BaseCommand,
    CommandInfo,
    ConfigField,
    register_plugin,
    send_api,
    chat_api,
)


class SayCommand(BaseCommand):
    """让bot说出指定内容（仅管理员可用）"""

    command_name = "say"
    command_description = "让bot说出指定的话（仅管理员可用）"
    command_pattern = r"^/say\s+(?P<enum>.+)+\s+(?P<num>.+)+\s+(?P<say_text>.+)$"

    async def execute(self) -> Tuple[bool, str, bool]:
        if (
            not self.message
            or not self.message.message_info
            or not self.message.message_info.user_info
            or str(self.message.message_info.user_info.user_id)
            not in self.get_config("plugin.admin_qq", [])
        ):
            return False, "没有权限", True

        enum = self.matched_group.get("enum", "").strip()
        num = self.matched_group.get("num", "").strip()
        text = self.matched_groups.get("say_text", "").strip()
        if (
            not enum
            or enum != "group" or"private"
        ):
            return False, "格式错误，请填写“group”获“private”" + "\n" +"格式为 /say group/private 100xxxx text" , True
        if(
            not num
            or not num.isdigit()
        ):
            return False, "格式错误，请填写正确的群号或者QQ号" + "\n" +"格式为 /say group/private 100xxxx text" , True
        if not text:
            return False, "内容为空" + "\n" +"格式为 /say group/private 100xxxx text", True

        stream_id = any
        if(enum == "group"):
            stream_id = get_stream_by_group_id(num)
        if(enum == "private"):
            stream_id = get_stream_by_user_id(num)

        if not stream_id:
            return False, "未找到对应的群号获QQ号" , True

        await self.text_to_stream(text, stream_id, True, False, None, True, None)
        return True, "已发送", True


@register_plugin
class SayPlugin(BasePlugin):
    """Say插件 - 让管理员通过命令让bot说出指定内容"""

    plugin_name: str = "say_plugin"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name: str = "config.toml"

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="1.0.0", description="配置文件版本"),
            "admin_qq": ConfigField(
                type=list,
                default=[],
                description='有权限使用 /say 命令的管理员QQ号列表（字符串形式，如 ["123456789"]）',
            ),
        },
    }

    def get_plugin_components(self) -> List[Tuple[CommandInfo, Type[BaseCommand]]]:
        if self.get_config("plugin.enabled", True):
            return [(SayCommand.get_command_info(), SayCommand)]
        return []
