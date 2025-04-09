import json
import time
from datetime import datetime

from ascript.android.system import Device, R

from .utils import Utils


class Server:
    cache = {}
    config = {}
    can_use_scenes = []
    active_scene = {"id": ""}

    def init_app():
        display = Device.display()
        width = display.widthPixels
        height = display.heightPixels
        if width > height:
            Utils.sys_info["vertical"] = False
        Utils.sys_info["screen_w"] = width
        Utils.sys_info["screen_h"] = height
        print(f"屏幕分辨率：{width}*{height} 横屏{not Utils.sys_info['vertical']}")
        Server.init_data()

    def init_data():
        """获取json文件的数据"""
        with open(R.res("/data/config.json"), encoding="utf-8") as f:
            Server.config = json.load(f)
        with open(R.res("/data/tpls.json"), encoding="utf-8") as f:
            Utils.tpls = json.load(f)
        with open(R.res("/data/cache.json"), encoding="utf-8") as f:
            Server.cache = json.load(f)

    def init_config():
        if "scenes" in Server.config:
            scenes = Server.config["scenes"]
            for scene in scenes:
                if scene["checked"]:
                    Server.can_use_scenes.append(scene)

    def init_cache(is_watch=False):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d")
        if "date" in Server.cache:
            date = Server.cache["date"]
            if is_watch:
                if date != formatted_time:
                    Server.cache = {"date": formatted_time}
            else:
                if date:
                    if date != formatted_time:
                        Server.cache = {"date": formatted_time}
        else:
            Server.cache = {"date": formatted_time}

    def switch_scene(win=None):
        """切换场景"""
        scenes = Server.can_use_scenes
        active_scene_id = Server.active_scene["id"]
        if len(scenes):
            un_filsh_scenes = []
            for scene in scenes:
                scene_id = scene["id"]
                if scene_id != active_scene_id:
                    if scene_id in Server.cache:
                        if not Server.cache[scene_id]["flish"]:
                            un_filsh_scenes.append(scene)
                    else:
                        un_filsh_scenes.append(scene)
            if len(un_filsh_scenes):
                Server.active_scene = un_filsh_scenes[0]
                return True
            elif not Server.cache[active_scene_id]["flish"]:
                return "replay"
            else:
                # 无可用场景，下线
                return "offline"
        else:
            if win:
                Utils.eval_js(win, "toast", "场景数据未开启!")
            return False

    def offline():
        """下线"""
        flag = Utils.clickByTpl("g_xtsz_btn", is_exc=False, i=3)
        if flag:
            Utils.randomSleep(1)
            Utils.clickByTpl("g_offline_rect")
            Utils.randomSleep(1)
            Utils.clickByTpl("g_offline_ok_rect")
            raise ValueError("下线成功")

    def get_location():
        txt = Utils.get_txt("location_rect")
        if txt:
            print(f"位置：{ txt[0].text}")
            return txt[0].text
        else:
            return False

    def handle_exc():
        print("处理异常中")
        Utils.click_by_rect("g_close")
        Utils.click_by_rect("g_close2")
        Utils.click_by_rect("g_l_gn_open")
        Utils.click_by_rect("g_pb_back")
        Server.close_bd_Tip()
        Utils.randomSleep(1)

    def close_bd_Tip():
        """关闭设备绑定的提醒"""
        txt = Utils.get_txt("tip_txt_rect", keys=["绑定", "快捷", "设备", "登录"])
        if txt:
            res = Utils.click_by_rect("g_close2")
            if res:
                print("检测到设备绑定提醒并且关闭了")
            else:
                print("检测到设备绑定提醒但是关闭失败了")

    def go_to_init_Map(target):
        """飞往场景的初始位置"""
        # 使用飞行符
        res = Server.use_dao_ju_by_img("dao_ju_fxf")
        # 不同的场景飞往不同的地方
        if res:
            Utils.click_by_rect(target)
        return res

    def open_dao_ju():
        is_show = Server.dao_ju_is_show()
        if is_show:
            return True
        else:
            res = Utils.click_by_rect("dao_ju_btn")
            if res:
                Utils.randomSleep(1)
            return res

    def dao_ju_is_show():
        """判断背包是否处于已打开状态"""
        txt = Utils.get_txt("dao_ju_title_rect", keys=["道", "具", "行", "囊"])
        if txt:
            return True
        else:
            return False

    def use_dao_ju_by_img(name):
        """使用道具"""
        # 先打开背包
        flag = False
        res = Server.open_dao_ju()
        if res:
            has_dj = Utils.click_by_rect(name)
            if has_dj:
                Utils.randomSleep(1)
                is_use = Utils.click_by_rect("dao_ju_use")
                if is_use:
                    Server.cache['last_use_syx'] = {
                        "scene_id": Server.active_scene['id'],
                        "time": time.time()
                    }
                    flag = True
        print(f"使用 {name} {flag}")
        return flag
