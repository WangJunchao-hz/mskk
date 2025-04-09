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
    tip_w = None
    tip_fun_name = None
    dao_ju_datas = None
    fire_num = 0
    is_js = False

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
            print(f"位置：{txt[0].text}")
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

    def get_pos_while(key, i=2, handle_exc=True):
        index = 1
        while True:
            if index <= i:
                res = Utils.get_pos(key)
                if res:
                    return res
                else:
                    if handle_exc and index == 1:
                        Server.handle_exc()
                    index = index + 1
            else:
                break
            Utils.randomSleep(1)

    def go_to_init_Map(target):
        """飞往场景的初始位置"""
        # 使用飞行符
        res = Server.use_dao_ju_by_img("dao_ju_fxf")
        # 不同的场景飞往不同的地方
        if res:
            Utils.randomSleep(1)
            is_open = Server.get_pos_while("fxf_map_flag", i=3, handle_exc=False)
            # print(f"{target} {is_open}")
            if is_open:
                Utils.click_by_rect(target)
                return True
            else:
                return False
        else:
            return False

    def open_dao_ju():
        is_show = Server.dao_ju_is_show()
        if is_show:
            return True
        else:
            res = Utils.click_by_rect("dao_ju_btn")
            if res:
                Utils.randomSleep(1)
                is_open = Server.dao_ju_is_show()
                if is_open:
                    return True
                else:
                    return False
            else:
                return False

    def close_dao_ju(is_check=True):
        """关闭背包"""
        res = False
        if is_check:
            is_show = Server.dao_ju_is_show()
            if is_show:
                res = Utils.click_by_rect("g_close")
            else:
                res = True
        else:
            res = Utils.click_by_rect("g_close")
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
                is_use = Utils.click_by_rect("dao_ju_use", click_time=(300, 600))
                # print(f"使用 {name} {click_time} {is_use}")
                if is_use:
                    if "syx" in name:
                        Server.cache["last_use_syx"] = {
                            "scene_id": Server.active_scene["id"],
                            "time": time.time(),
                            "expire": False,
                        }
                        Utils.save_json("cache", Server.cache)
                    flag = True
        return flag

    def use_syx():
        if "last_use_syx" in Server.cache:
            last_syx = Server.cache["last_use_syx"]
            if "expire" in last_syx and last_syx["expire"]:
                flag = Server.use_dao_ju_by_img("dao_ju_syx")
                if flag:
                    # 使用后关闭背包
                    Server.close_dao_ju(False)
                    # 等地图完全关闭
                    Utils.randomSleep(1)
                return flag
            else:
                dif = time.time() - last_syx["time"]
                # print(f"last_use_syx: {last_syx} {dif}")
                if dif > Server.config["syx_time"]:
                    Server.push_log(log="摄妖香失效了，重新吃")
                    flag = Server.use_dao_ju_by_img("dao_ju_syx")
                    if flag:
                        # 使用后关闭背包
                        Server.close_dao_ju(False)
                        # 等地图完全关闭
                        Utils.randomSleep(1)
                    return flag
                else:
                    log = f"摄妖香没失效，已经过了{dif/60:.2f}分钟"
                    Server.push_log(log=log)
                    print(log)
                    return True
        else:
            # print("un_use_syx")
            Server.push_log(log="第一次吃摄妖香")
            flag = Server.use_dao_ju_by_img("dao_ju_syx")
            if flag:
                # 使用后关闭背包
                Server.close_dao_ju(False)
                # 等地图完全关闭
                Utils.randomSleep(1)
            return flag

    def open_map():
        hasMap = Utils.get_pos("map_flag")
        if not hasMap:
            hasMap = Utils.get_pos("map_flag2")
        if not hasMap:
            Utils.click_by_rect("map_rect")
            Utils.randomSleep(1)
            is_open = Utils.get_pos("map_flag")
            if not is_open:
                is_open = Utils.get_pos("map_flag2")
            if is_open:
                return True
            else:
                return False
        else:
            return True

    def close_map(is_check=True):
        if is_check:
            hasMap = Utils.get_pos("map_flag")
            if not hasMap:
                hasMap = Utils.get_pos("map_flag2")
            if hasMap:
                is_close = Utils.click_by_rect("g_close")
                if not is_close:
                    Utils.click_by_rect("map_close_rect")
        else:
            is_close = Utils.clickByTpl("g_close")
            if not is_close:
                Utils.clickByTpl("map_close_rect")

    def guo_map(name, callback):
        """通用的过图场景"""
        # 先点开地图
        # print("打开地图")
        is_open = Server.open_map()
        if is_open:
            # 点击要去的坐标
            Utils.click_by_rect(name)
            Utils.randomSleep(1)
            # 关闭地图
            Server.close_map()
            Utils.randomSleep(1)
            lasPos = None
            while True:
                txt = Utils.get_txt("map_rect")
                if txt:
                    if lasPos == txt[0].text:
                        print("停止移动了")
                        return callback()
                    else:
                        lasPos = txt[0].text
                Utils.randomSleep(1)
        else:
            return False

    def push_log(log="", zj=""):
        if Server.tip_fun_name:
            data = {"zhan_ji": zj, "log": log}
            Utils.eval_js(Server.tip_w, Server.tip_fun_name, data)

    def is_firing():
        is_hh = False
        txt = Utils.get_txt("fire_hh_rect", keys=["第", "回", "合"])
        if txt:
            is_hh = True
        flag1 = Utils.get_pos("firing_flag")
        flag2 = Utils.get_pos("fire_target_flag")
        flag3 = Utils.get_pos("jn_mskk")
        if is_hh or flag1 or flag2 or flag3:
            return {"mskk": flag3}
        else:
            return False

    def init_bei_bao():
        """初始化背包数据"""
        is_open = Server.open_dao_ju()
        if is_open:
            Server.dao_ju_datas = Utils.get_dj_datas()
            log = f"道具识别完成：金币：{Server.dao_ju_datas['money']}，普通道具{len(Server.dao_ju_datas['dj'])}个，叠加道具{len(Server.dao_ju_datas['dj_num'])}个，空道具栏{len(Server.dao_ju_datas['blank'])}个"
            print(log)
            Server.push_log(log=log)
            if len(Server.dao_ju_datas["blank"]) == 0:
                Server.move_dao_ju()
            Server.close_dao_ju(False)
            Utils.randomSleep(1)

    def get_qx_status(is_fire=False):
        if Server.is_js:
            # 刚进行过酒肆，直接返回True
            print("刚进行过酒肆，满状态")
            if is_fire:
                Server.is_js = False
            return True
        else:
            need_xue = False
            need_lan = False
            xue_per = Utils.get_qi_xue_by_colors()
            lan_per = Utils.get_mo_li_by_colors()
            print(f"血量{xue_per*100}% 蓝量{lan_per*100}%")
            if xue_per < Server.config["base"]["xue"]:
                need_xue = True
                print(f"没血了，快补血({xue_per*100}%)")
            if lan_per < Server.config["base"]["lan"]:
                need_lan = True
                print(f"没蓝了，快补蓝({lan_per*100}%)")
            if need_xue or need_lan:
                return False
            else:
                return True

    def bu_xue():
        Utils.click_by_rect("g_l_gn")
        Utils.randomSleep(1)
        has_hllb = Server.get_pos_while("g_hllb", i=60, handle_exc=False)
        if has_hllb:
            Utils.click_by_pos(has_hllb)
            Utils.randomSleep(1)
        else:
            return False


        is_open = False
        Utils.clickByTpl("g_l_gn")
        index = 1
        while True:
            if index <= i:
                is_open = Utils.getPos("g_l_gn_open", i=60, sleep=1)
                if not is_open:
                    Utils.clickByTpl("g_l_gn")
                    index = index + 1
                else:
                    break
            else:
                raise ValueError("补血失败")
                break
            Utils.randomSleep(1)
        has_hllb = Utils.clickByTpl("g_hllb", i=666, sleep=1)
        # print("进行补给", has_hllb)
        if has_hllb:
            Utils.randomSleep(1)
            has_js = Utils.clickByTpl("g_hllb_js", i=100, sleep=1)
            if has_js:
                Utils.randomSleep(1)
                Utils.clickByTpl("g_js_xx")
                Operate.dj_change["total_js"] = Operate.dj_change["total_js"] + 1
                Operate.dj_change["js"] = 1
                Operate.new_dj_datas["money"] = Operate.new_dj_datas["money"] - 1000
                Utils.operate_cache["is_js"] = True
                print(f'进行一次酒肆金币减1000，余额：{Operate.new_dj_datas["money"]}')
                Utils.randomSleep(1)
                Utils.clickByTpl("g_close", is_exc=True, need_stop=False)
                Utils.randomSleep(1)
                has_gn_open = Utils.clickByTpl(
                    "g_l_gn_open", i=100, is_exc=True, need_stop=False, sleep=1
                )
                if has_gn_open:
                    Utils.randomSleep(2)

    def start_tou_ka():
        is_fire = Server.is_firing()
        if is_fire:
            Server.push_log(log="检测到战斗")
            print("检测到战斗")
            Server.fire_num = Server.fire_num + 1
        else:
            if not Server.dao_ju_datas:
                # 初始化背包数据
                Server.init_bei_bao()
            if Server.get_qx_status():
                print('补血')
            
