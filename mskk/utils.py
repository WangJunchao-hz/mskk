import json
import random
import time

from ascript.android import action, system
from ascript.android.screen import FindImages, Ocr
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
                res = FindImages.find_template(
                    R.img(rect), confidence=confidence)
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

    def click_by_rect(key, is_all=False, confidence=0.90, is_center=False):
        pos = Utils.get_pos(key, is_all, confidence, is_center)
        if pos:
            Utils.click_by_pos(pos)
            return True
        else:
            return False

    def click_by_pos(pos):
        action.click(pos[0], pos[1])

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
        return is_success

    def get_tpl(key):
        if isinstance(key, str):
            key = f"{key}_{Utils.sys_info['screen_w']}"
            return Utils.tpls[key]
        else:
            return key
