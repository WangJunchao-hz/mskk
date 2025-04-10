import json
import os
import random
import re
import time

from ascript.android import action, screen, system
from ascript.android.screen import Colors, FindColors, FindImages, Ocr
from ascript.android.system import R


class Utils:
    tpls = {}
    sys_info = {
        "screen_w": 1920,
        "screen_h": 1080,
        "vertical": True,
        "screen_change": False,
    }

    def dict_to_json(dict_data):
        return json.dumps(dict_data, ensure_ascii=False, indent=4)

    def json_to_dict(json_str):
        return json.loads(json_str)

    def save_json(name, data):
        with open(R.res(f"/data/{name}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)  # 更易读且支持中文

    def randomSleep(t=None, r=(1, 3)):
        """随机延迟模拟人的行为"""
        if t:
            time.sleep(t)
        else:
            t = random.randint(r[0], r[1])
            time.sleep(t)
        # print(f'Utils.randomSleep延迟 {t} 秒')

    def eval_js(win, name, data):
        data = Utils.dict_to_json(data)
        win.call(f"{name}({data})")

    def app_exit():
        system.exit()

    def get_random_pos(rect):
        """随机坐标模拟人的行为"""
        rx = random.randint(rect[0], rect[2])
        ry = random.randint(rect[1], rect[3])
        return (rx, ry)

    def get_random(range):
        return random.randint(range[0], range[1])

    def get_center_pos(rect):
        """获取中心点坐标"""
        cx = int((rect[0] + rect[2]) / 2)
        cy = int((rect[1] + rect[3]) / 2)
        return (cx, cy)

    def get_pos(key, is_all=False, confidence=0.90, is_center=False):
        rect = Utils.get_tpl(key)
        if isinstance(rect, str):
            res = None
            if is_all:
                res = FindImages.find(R.img(rect), confidence=confidence)
            else:
                res = FindImages.find_template(R.img(rect), confidence=confidence)
            if res:
                rect = res["rect"]
            else:
                rect = False
        if rect:
            if is_center:
                return Utils.get_center_pos(rect)
            else:
                return Utils.get_random_pos(rect)
        else:
            return False

    def click_by_rect(
        key, is_all=False, confidence=0.90, is_center=False, click_time=None
    ):
        pos = Utils.get_pos(key, is_all, confidence, is_center)
        if pos:
            Utils.click_by_pos(pos, click_time)
            return True
        else:
            return False

    def click_by_pos(pos, click_time=(100, 300)):
        time = 20
        if click_time:
            if type(click_time) == int:
                time = click_time
            else:
                time = Utils.get_random(click_time)
        else:
            time = Utils.get_random((100, 300))
        action.click(pos[0], pos[1], time)

    def get_txt(key, t=0, keys=[]):
        """识别文字 0=google, 1=百度v2, 2=TesserAct"""
        rect = Utils.get_tpl(key)
        res = None
        if t == 0:
            res = Ocr.mlkitocr_v2(rect=rect)
        if t == 1:
            res = Ocr.paddleocr_v2(rect=rect)
        if t == 2:
            res = Ocr.tess(rect=rect, data_file=Ocr.Tess_ENG)
        is_success = False
        if res and len(res):
            is_success = res
            if len(keys):
                flag = False
                for item in res:
                    txt = item.text
                    if txt and any(k in txt for k in keys):
                        flag = True
                        break
                if not flag:
                    is_success = False
                if key == 'fire_jc_txt':
                    print('is_success',flag,is_success)
        return is_success

    def get_tpl(key):
        if isinstance(key, str):
            key = f"{key}_{Utils.sys_info['screen_w']}"
            return Utils.tpls[key]
        else:
            return key

    def get_dj_boxs():
        """获取道具格子坐标"""
        # 将内存截图Bitmap转换为cv img
        # img = screen.bitmap_to_cvimage()
        firstPos = Utils.get_tpl("g_dj_first_box")
        # 默认是1920的数值
        borderw = 6
        borderh = 6
        w = 130
        h = 130
        if Utils.sys_info["screen_w"] == 2280:
            borderw = 4
        fx = firstPos[0]
        fy = firstPos[1]
        boxs = []
        for i in range(0, 4):
            for j in range(0, 5):
                x = fx + w * j + borderw * j
                y = fy + h * i + borderh * i
                x1 = x + w
                y1 = y + h
                boxs.append(
                    {
                        "rect": [x, y, x1, y1],
                        "hotRect": [x + 6, y + 6, x1 - 6, y1 - 6],
                        "centerRect": [x + 50, y + 50, x1 - 50, y1 - 50],
                        "numRect": [x, y, x + 100, y + 100],
                        "index": f"{i+1}_{j+1}",
                        "name": "",
                        "num": "",
                        "type": "",
                        "can_move": True,
                        "is_card": False,
                    }
                )
                # sx = x
                # sy = y
                # sp = img[sy:y1, sx:x1]
                # goodPath = R.img(f"boxs/{i}_{j}.png")
                # cv2.imwrite(goodPath, sp)
        return boxs

    def check_has_dao_ju(box):
        count = Colors.count("#B8B0D8", rect=box["centerRect"])
        return count < 900

    def get_num_by_str(text):
        num_match = re.search(r"\d+", text)
        if num_match:
            return int(num_match.group())
        else:
            return 0

    def get_single_dao_ju_data(box, is_num=False, get_type=False):
        """ "根据道具位置信息获取道具详情"""
        res = {}
        new_box = box.copy()

        def get_num():
            num_txt = Utils.get_txt(box["numRect"])
            # print(new_box["name"], num_txt)
            if num_txt:
                new_box["num"] = Utils.get_num_by_str(num_txt[0].text)
                if new_box["num"]:
                    res["type"] = "dj_num"
                # print(f"{new_box['name']}:{new_box['num']}")

        if is_num:
            get_num()
        else:
            if Utils.check_has_dao_ju(box):
                res["type"] = "dj"
                if get_type:
                    Utils.click_by_rect(box["hotRect"])
                    Utils.randomSleep(1)
                    txt = Utils.get_txt("dao_ju_name_rect", t=1)
                    if txt:
                        new_box["name"] = txt[0].text
                        if "卡" in new_box["name"]:
                            new_box["is_card"] = True
                        elif get_type:
                            des_txt = Utils.get_txt(
                                "dao_ju_des_rect", t=1, keys=["装", "备"]
                            )
                            # print(des_txt)
                            if des_txt:
                                new_box["type"] = "装备"
                else:
                    get_num()
            else:
                res["type"] = "blank"
        res["data"] = new_box
        return res

    def get_money():
        """获取金币数量"""
        # 点击一下空白处防止识别失败
        Utils.click_by_rect("g_dao_ju_blank")
        Utils.randomSleep(1)
        moneyTxt = Utils.get_txt("g_money")
        if moneyTxt:
            return Utils.get_num_by_str(moneyTxt[0].text)
        else:
            print("获取金币失败")
            return False

    def get_dj_datas():
        blank = []
        dao_ju = []
        dao_ju_has_num = []
        boxs = Utils.get_dj_boxs()
        for box in boxs:
            item = Utils.get_single_dao_ju_data(box)
            if item["type"] == "dj":
                dao_ju.append(item["data"])
            elif item["type"] == "dj_num":
                dao_ju_has_num.append(item["data"])
            elif item["type"] == "blank":
                blank.append(item["data"])
        return {
            "dj": dao_ju,
            "dj_num": dao_ju_has_num,
            "blank": blank,
            "money": Utils.get_money(),
        }

    def get_qi_xue_by_colors():
        rect = Utils.get_tpl("g_xue_rect")
        flag_color = "1915,6,#B23C2F-#0b0409"
        if Utils.sys_info["screen_w"] == 2280:
            flag_color = "2146,7,#C14E42-#0f161c"
        point = FindColors.find(
            flag_color,
            rect=rect,
        )
        total = rect[2] - rect[0]
        if point:
            sy = (point.x + 1) - rect[0]
            return round(sy / total, 2)
        else:
            has = FindColors.find("1820,11,#EB452C-#011f2a", rect=rect)
            if has:
                return 1
            else:
                return 0

    def get_mo_li_by_colors():
        rect = Utils.get_tpl("g_lan_rect")
        flag_color = "1891,24,#6897CA-#0c0806"
        if Utils.sys_info["screen_w"] == 2280:
            flag_color = "2097,25,#6B97C7-#0a0402"
        point = FindColors.find(
            flag_color,
            rect=rect,
        )
        total = rect[2] - rect[0]
        if point:
            sy = (point.x + 1) - rect[0]
            return round(sy / total, 2)
        else:
            has = FindColors.find("1822,30,#4798E7-#291402", rect=rect)
            if has:
                return 1
            else:
                return 0

    def saveImg(name, dirName):
        """保存图片至sd卡"""
        print(R.sd(f"{dirName}/{name}.png"))
        screen.bitmap_to_file(R.sd(f"{dirName}/{name}.png"))

    def mkSDDir(name):
        """在sd卡创建一个文件夹"""
        path = R.sd(name)
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"Utils.mkSDDir文件夹{name}创建成功")
        else:
            print(f"Utils.mkSDDir文件夹{name}已存在")

    def is_include(a, b, qz=(10, 10)):
        """判断a是否在b中某个坐标附近 默认在附近20坐标差"""
        flag = False
        if a and b:
            for p in b:
                difX = abs(a[0] - p[0])
                difY = abs(a[1] - p[1])
                if difX <= qz[0] and difY <= qz[1]:
                    flag = True
                    break
        return flag
