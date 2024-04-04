from flask import Flask, request, jsonify
import requests
import ipaddress

from app.core.config import settings
from app.core.event import eventmanager, Event
from app.log import logger
from app.modules.emby import Emby
from app.modules.jellyfin import Jellyfin
from app.modules.plex import Plex
from app.modules.qbittorrent import Qbittorrent
from app.modules.transmission import Transmission
from app.plugins import _PluginBase
from app.schemas import NotificationType, WebhookEventInfo
from app.schemas.types import EventType
from app.utils.ip import IpUtils

class SpeedLimiter(_PluginBase):
    # 插件名称
    plugin_name = "播放限速"
    # 插件描述
    plugin_desc = "外网播放媒体库视频时，自动对下载器进行限速。"
    # 插件图标
    plugin_icon = "Librespeed_A.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "Shurelol"
    # 作者主页
    author_url = "https://github.com/Shurelol"
    # 插件配置项ID前缀
    plugin_config_prefix = "speedlimit_"
    # 加载顺序
    plugin_order = 11
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None
    _qb = None
    _tr = None
    _enabled: bool = False
    _notify: bool = False
    _interval: int = 60
    _downloader: list = []
    _play_up_speed: float = 0
    _play_down_speed: float = 0
    _noplay_up_speed: float = 0
    _noplay_down_speed: float = 0
    _bandwidth: float = 0
    _allocation_ratio: str = ""
    _auto_limit: bool = False
    _limit_enabled: bool = False
    # 不限速地址
    _unlimited_ips = {}
    # 当前限速状态
    _current_state = ""
