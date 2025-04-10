import json
import time
from datetime import datetime

from ascript.android import plug
from ascript.android.system import Device, R

from .utils import Utils

# 加载yolov8插件
plug.load("Yolov8Ncnn:1.7")  # 这里请更换最新版本 在插件列表里面查看
import Yolov8Ncnn as yolo


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
    last_map_i = -1
    dj_change = {"money": "", "dj": []}
    first_run = True

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
        Utils.mkSDDir(Server.config["dirName"])

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
                a_s = un_filsh_scenes[0]
                if (
                    Server.first_run
                    and "last_id" in Server.cache
                    and Server.cache["last_id"]
                ):
                    print(f'last_id：{Server.cache["last_id"]}')
                    for s in un_filsh_scenes:
                        if s["id"] == Server.cache["last_id"]:
                            a_s = s
                            break
                Server.active_scene = a_s
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
        flag = Utils.click_by_rect("g_xtsz_btn", is_exc=False, i=3)
        if flag:
            Utils.randomSleep(1)
            Utils.click_by_rect("g_offline_rect")
            Utils.randomSleep(1)
            Utils.click_by_rect("g_offline_ok_rect")
            Utils.app_exit()

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

    def is_firing(i=1):
        index = 1
        while True:
            if index <= i:
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
                    index = index + 1
            else:
                return False

    def move_dao_ju():
        """移动道具"""
        Server.xn_full = False

        def move_single_dao_ju(box):
            if not Server.xn_full:
                has_dj = Utils.check_has_dao_ju(box)
                if has_dj:
                    Utils.click_by_rect(box["hotRect"])
                    Utils.randomSleep(1)
                    txt = Utils.get_txt("dao_ju_name_rect", t=1)
                    if txt and any(k in txt[0].text for k in ["香", "符", "草"]):
                        return False
                    Utils.click_by_rect("dao_ju_move")
                    Utils.randomSleep(1)
                    Utils.click_by_rect("g_dao_ju_xn")
                    Utils.randomSleep(1)
                    Server.xn_full = Utils.get_pos("dao_ju_xn_flag")
                    # print('xn_full:',self.xn_full)
                    if not Server.xn_full:
                        has = Utils.check_has_dao_ju(box)
                        if has:
                            print(f"此物品{box['index']}不能移动")
                            return False
                        else:
                            return True
                    else:
                        return False
                else:
                    return True
            else:
                return False

        blank = []
        dj = []
        dj_num = []

        for dj_box in Server.dao_ju_datas["dj"]:
            if not Server.xn_full:
                can_move = dj_box["can_move"]
                if can_move is False:
                    dj.append(dj_box)
                else:
                    is_move = move_single_dao_ju(dj_box)
                    if not Server.xn_full:
                        if is_move:
                            dj_box["name"] = ""
                            dj_box["num"] = ""
                            blank.append(dj_box)
                        else:
                            dj_box["can_move"] = False
                            dj.append(dj_box)
                    else:
                        dj.append(dj_box)
            else:
                dj.append(dj_box)

        for num_box in Server.dao_ju_datas["dj_num"]:
            if not Server.xn_full:
                can_move = num_box["can_move"]
                if can_move is False:
                    dj_num.append(num_box)
                else:
                    is_move = move_single_dao_ju(num_box)
                    if not Server.xn_full:
                        if is_move:
                            num_box["name"] = ""
                            num_box["num"] = ""
                            blank.append(num_box)
                        else:
                            num_box["can_move"] = False
                            dj_num.append(num_box)
                    else:
                        dj_num.append(num_box)
            else:
                dj_num.append(num_box)

        Server.dao_ju_datas["dj"] = dj
        Server.dao_ju_datas["dj_num"] = dj_num
        Server.dao_ju_datas["blank"] = blank
        if len(blank) == 0:
            # 停止脚本运行或下线
            print("装不下了，要下线")
            Server.offline()
        if Server.xn_full:
            print("行囊满了")
            Utils.click_by_rect("g_dao_ju_dj")
            Utils.randomSleep(1)
            Utils.click_by_rect("g_dao_ju_dj")
            Utils.randomSleep(1)
            # 因为格子乱了，所以需要重新初始化
            Server.init_bei_bao()
        print(f"道具移动完成，剩余{len(blank)}个格子")

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
        is_open = Utils.get_pos("g_l_gn_open")
        if not is_open:
            Utils.click_by_rect("g_l_gn")
            Utils.randomSleep(1)
        has_hllb = Utils.get_pos("g_hllb")
        if has_hllb:
            Utils.click_by_pos(has_hllb)
            Utils.randomSleep(1)
            has_js = Utils.get_pos("g_hllb_js")
            if has_js:
                Utils.click_by_pos(has_js)
                Utils.randomSleep(1)
                Utils.click_by_rect("g_js_xx")
                Server.dao_ju_datas["money"] = Server.dao_ju_datas["money"] - 1000
                Server.is_js = True
                log = f'进行一次酒肆金币减1000，余额：{Server.dao_ju_datas["money"]}'
                print(log)
                Server.push_log(log=log)
                Utils.randomSleep(1)
                is_close = Utils.click_by_rect("g_close")
                if is_close:
                    Utils.randomSleep(1)
                    Utils.click_by_rect("g_l_gn_open")
                    Utils.randomSleep(1)
                else:
                    return False
            else:
                return False
        else:
            return False

    def random_run_map(rect):
        """随机点地图遇怪"""
        # 先点开地图
        is_open = Server.open_map()
        # 点击要去的坐标
        if is_open:
            rects = Utils.get_tpl(rect)
            index = Utils.get_random((0, len(rects) - 1))
            while True:
                if index == Server.last_map_i:
                    index = Utils.get_random((0, len(rects) - 1))
                else:
                    Server.last_map_i = index
                    break
            Utils.click_by_rect(rects[index])
            # 关闭地图
            Utils.randomSleep(1)
            Server.close_map()
            return True
        else:
            return False

    def saveImg(type="fire"):
        # 先截图保存用于训练数据
        # 格式化当前时间
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H-%M-%S")
        sceneId = Server.active_scene["id"]
        imgName = f"{sceneId}_{type}_{formatted_time}"
        Utils.saveImg(imgName, Server.config["dirName"])

    def check_is_jc():
        """判断是否遇到检测"""
        print("判断是否遇到检测")
        while True:
            has_jc_txt = Utils.get_txt(
                "fire_jc_txt",
                keys=["恭喜", "面对", "意外", "奖励", "角色", "关闭", "窗口"],
            )
            if has_jc_txt:
                print(f"人机检测: {has_jc_txt[0].text}")
                # 等画面完全出来
                Utils.randomSleep(1)
                Server.saveImg("jc")
                Server.handle_jc()
            else:
                return False

    def handle_jc(i=-1):
        # 在屏幕上绘制目标
        yolo.draw(True, 5000)
        jc_model = Server.config["jc_model"]
        nc = jc_model["nc"]
        names = jc_model["names"]
        is_init = yolo.load(R.res(jc_model["param"]), R.res(jc_model["bin"]), nc)
        if is_init:
            res = yolo.detect()
            # print(f"检测模型识别成功{res}")
            if res and len(res):
                minC = {"c": 0, "pos": None}
                hasClick = False
                index = 0
                for r in res:
                    if r["class_id"] < len(names):
                        name = names[r["class_id"]]
                        x = int((r["rect"][0] + r["rect"][2]) / 2)
                        y = r["rect"][3] - 30
                        pos = (x, y)
                        # pos = Utils.getCenterPos(r["rect"])
                        if name == "面对":
                            print(f"点击：{r['class_id']}_{name}_{r['confidence']}")
                            Utils.click_by_pos(pos)
                            hasClick = True
                        else:
                            print(
                                f"检测识别成功：{r['class_id']}_{name}_{r['confidence']}"
                            )
                            if i != -1:
                                if index == i:
                                    minC["c"] = r["confidence"]
                                    minC["pos"] = pos
                            elif minC["c"] == 0 or minC["c"] > r["confidence"]:
                                minC["c"] = r["confidence"]
                                minC["pos"] = pos
                            index = index + 1
                if not hasClick and minC["pos"]:
                    print("点击：", minC)
                    Utils.click_by_pos(minC["pos"])
            yolo.free()

    def get_gw_pos():
        """识别并获取怪物的位置"""
        if Server.active_scene["id"] not in ["feng5", "feng6", "long5"]:
            self.saveImg()
        pt = []
        bb = []
        tp = False
        nc = Server.active_scene["yolo"]["nc"]
        if nc != 0:
            model = Server.active_scene["yolo"]["model"]
            names = Server.active_scene["yolo"]["names"]
            # 在屏幕上绘制目标
            yolo.draw(True, 5000)
            is_init = yolo.load(R.res(model["param"]), R.res(model["bin"]), nc)
            if is_init:
                # print("怪物模型初始化成功")
                res = yolo.detect()
                if res:
                    # print(f"模型识别成功{res}")
                    for r in res:
                        r["name"] = names[r["class_id"]]
                        if r["confidence"] > 0.4:
                            x = int((r["rect"][0] + r["rect"][2]) / 2)
                            y = r["rect"][3] - Server.active_scene["offset_gw"]
                            r["pos"] = (x, y)
                            pt.append(r)
                yolo.free()
        # 去识别宝宝
        fireTxt = Utils.get_txt("fire_txt_rect", t=1)
        if fireTxt:
            for gw_txt in fireTxt:
                item = {
                    "text": gw_txt.text,
                    "confidence": gw_txt.confidence,
                    "center_x": gw_txt.center_x,
                    "center_y": gw_txt.center_y,
                    "pos": (
                        gw_txt.center_x,
                        gw_txt.center_y - Server.active_scene["offset_gw"],
                    ),
                }
                # print("gw_txt", item)
                if "宝" in item["text"]:
                    print(f"发现一只宝宝{item}")
                    item["pos"] = (
                        gw_txt.center_x,
                        gw_txt.center_y - Server.active_scene["offset_bb"],
                    )
                    bb.append(item)
                elif nc == 0 and any(
                    k in item["text"] for k in Server.active_scene["keys"]
                ):
                    pt.append(item)

                if (
                    "tp_keys" in Server.active_scene
                    and len(Server.active_scene["tp_keys"])
                    and any(k in item["text"] for k in Server.active_scene["tp_keys"])
                ):
                    tp = True
        if len(pt) or len(bb):
            return {"pt": pt, "bb": bb, "tp": tp}
        else:
            return False

    def fire(mskk_pos):
        has_click_gw = []
        # 1=正常战斗完 0=要补给了 2=逃跑了
        status = 1
        while True:
            if not mskk_pos:
                is_fire = Server.is_firing(2)
                print("is_fire", is_fire)
                if is_fire:
                    mskk_pos = is_fire["mskk"]
                else:
                    return status
            else:
                if Server.get_qx_status(True):
                    print("去识别怪物")
                    res = Server.get_gw_pos()
                    if res:
                        if res["tp"]:
                            Utils.click_by_rect("jn_tao_pao")
                            status = 2
                        else:
                            if len(res["bb"]):
                                # 全力抓宝宝
                                for b in res["bb"]:
                                    # 点击捕捉
                                    Utils.click_by_rect("jn_bz")
                                    Utils.randomSleep(1)
                                    # 点击宝宝
                                    Utils.click_by_pos(b["pos"])
                                    print("抓宝宝中...")
                                    # 一次只能抓一次宝宝，所以需要break
                                    break
                            else:
                                hasTT = []
                                for g in res["pt"]:
                                    pos = g["pos"]
                                    if not Utils.is_include(pos, has_click_gw):
                                        # 点击妙手空空
                                        Utils.click_by_pos(mskk_pos)
                                        Utils.randomSleep(1)
                                        Utils.click_by_pos(pos)
                                        # print(f"已偷的怪：{g}")
                                        has_click_gw.append(pos)
                                        break
                                    else:
                                        hasTT.append(g)
                                if len(hasTT) == len(res["pt"]):
                                    print("都偷完了要逃跑")
                                    # 赶紧逃跑
                                    Utils.click_by_rect("jn_tao_pao")
                                    status = 1
                    else:
                        print("未识别到怪物")
                        Utils.click_by_rect("jn_tao_pao")
                        status = 2
                else:
                    Utils.click_by_rect("jn_tao_pao")
                    status = 0
                mskk_pos = None

    def start_tou_ka(rect):
        is_run = False
        last_pos = None
        while True:
            is_fire = Server.is_firing()
            if is_fire:
                Server.push_log(log="检测到战斗")
                print("检测到战斗")
                Server.fire(is_fire["mskk"])
                print("战斗结束")
                Server.fire_num = Server.fire_num + 1
                if Server.fire_num == Server.config["base"]["check_dao_ju"]:
                    # 检测背包
                    Server.check_bei_bao()
                    Server.fire_num = 0
                Server.check_status()
                is_run = False
            else:
                if is_run:
                    Server.check_is_jc()
                if not Server.dao_ju_datas:
                    # 初始化背包数据
                    Server.init_bei_bao()
                if not is_run and not Server.get_qx_status():
                    is_full = Server.bu_xue()
                    if not is_full:
                        Server.handle_exc()
                else:
                    # 随机遇怪
                    if not is_run:
                        is_run = Server.random_run_map(rect)
                    else:
                        # 检测是否停止了
                        txt = Utils.get_txt("map_rect")
                        if txt:
                            if last_pos == txt[0].text:
                                print("停止移动了")
                                break
                            else:
                                # print("移动中...")
                                last_pos = txt[0].text

    def check_status():
        # 时间到了，要切换场景
        scene_id = Server.active_scene["id"]
        start_time = Server.active_scene["start_time"]
        current_time = time.time()
        dif = current_time - start_time
        if (
            Server.first_run
            and "last_time" in Server.cache
            and "last_id" in Server.cache
            and Server.cache["last_id"] == scene_id
        ):
            dif = dif + Server.cache["last_time"]
        log = f'{Server.active_scene["name"]}场景已经偷了{dif/3600:.2f}小时，{dif/60:.2f}分钟，{dif:.2f}秒'
        print(log)
        Server.push_log(log=log)
        is_time_over = False
        if Server.active_scene["time"] > 0 and dif >= Server.active_scene["time"]:
            print("时间到了，要切换场景")
            Server.active_scene["stop"] = True
            is_time_over = True
        Server.cache["last_id"] = scene_id
        if is_time_over:
            Server.cache["last_time"] = 0
            if scene_id in Server.cache:
                Server.cache[scene_id]["time_over_num"] = (
                    Server.cache[scene_id]["time_over_num"] + 1
                )
            else:
                Server.cache[scene_id] = {
                    "hz": [],
                    "flish": False,
                    "time_over_num": 1,
                }
        else:
            Server.cache["last_time"] = dif

        Utils.save_json("cache", Server.cache)
        is_flish = Server.cache[scene_id]["flish"]
        if is_flish:
            # 当前场景偷满了，要切换场景
            print("当前场景偷满了，要切换场景")
            Server.active_scene["stop"] = True
        if len(Server.dao_ju_datas["blank"]) == 0:
            # 装备满了要移走
            print("装备满了快移走")
            Server.move_dao_ju()
        # 都偷满了，下线
        if Server.cache["total_hz"] >= 12:
            print("都偷满了，下线")
            Server.offline()

    def check_bei_bao():
        """检测背包"""
        Server.open_dao_ju()
        Server.dj_change["dj"] = []
        # 先查看金币的变化
        oldMoney = Server.dao_ju_datas["money"]
        newMoney = Utils.get_money()
        if newMoney:
            dif = newMoney - oldMoney
            Server.dj_change["money"] = f"金币变化：{dif}"
            Server.dao_ju_datas["money"] = newMoney

        new_blank = []
        huan_zhuang = []
        card_num = 0
        # 查看空栏有没有新增装备
        blank = Server.dao_ju_datas["blank"]
        for box in blank:
            item = Utils.get_single_dao_ju_data(box, get_type=True)
            if item["data"]["is_card"]:
                card_num = card_num + 1
            name = item["data"]["name"]
            num = item["data"]["num"]
            index = item["data"]["index"]
            if item["type"] == "dj":
                Server.dao_ju_datas["dj"].append(item["data"])
                Server.dj_change["dj"].append(f"{index}:{name}")
                if item["data"]["type"] == "装备":
                    huan_zhuang.append(f"{index}:{name}")
            elif item["type"] == "dj_num":
                Server.dao_ju_datas["dj_num"].append(item["data"])
                Server.dj_change["dj"].append(f"{index}:{name}({num})")
            else:
                new_blank.append(item["data"])
        # 更新空白栏数据
        Server.dao_ju_datas["blank"] = new_blank
        # 查看叠加道具有没有新增
        dj_num = Server.dao_ju_datas["dj_num"]
        for box in dj_num:
            oldNum = box["num"]
            item = Utils.get_single_dao_ju_data(box, True)
            newBox = item["data"]
            index = newBox["index"]
            newNum = newBox["num"]
            dif = newNum - oldNum
            if dif:
                box["num"] = newNum
                Server.dj_change["dj"].append(f"{index}:叠加道具({dif})")

        log = f'{Server.dj_change["money"]}，新增道具：{Server.dj_change["dj"]}'
        print(log)
        Server.push_log(log=log)
        scene_id = Server.active_scene["id"]
        if scene_id in Server.cache:
            Server.cache[scene_id]["hz"] = Server.cache[scene_id]["hz"] + huan_zhuang
        else:
            Server.cache[scene_id] = {
                "hz": huan_zhuang,
                "flish": False,
                "time_over_num": 0,
            }
        if len(Server.cache[scene_id]["hz"]) >= 4:
            Server.cache[scene_id]["flish"] = True
        if "total_hz" in Server.cache:
            Server.cache["total_hz"] = Server.cache["total_hz"] + len(huan_zhuang)
        else:
            Server.cache["total_hz"] = len(huan_zhuang)
        if "card_num" in Server.cache:
            Server.cache["card_num"] = Server.cache["card_num"] + card_num
        else:
            Server.cache["card_num"] = card_num

        zj = f'已经偷了{Server.cache["total_hz"]}个环状，{Server.cache["card_num"]}张卡'
        print(zj)
        Server.push_log(zj=zj)
        Server.close_dao_ju(False)
        Utils.randomSleep(1)
