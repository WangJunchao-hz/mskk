import time

from ascript.android import screen
from ascript.android.system import R
from ascript.android.ui import WebWindow

from .scenes.long5 import Long5
from .server import Server
from .utils import Utils

long5 = Long5()


class Main:
    tip_fun_name = ""
    Win = None
    is_win_close = False
    Tip_win = None
    sceneDict = {
        "long5": long5.initScene,
        # "long6": long6.initScene,
        # "feng6": feng6.initScene,
        # "feng5": feng5.initScene,
        # "wmgc": wmgc.initScene,
        # "qls": qls.initScene,
        # "zmhd": zmhd.initScene
    }

    def __init__(self):
        """实例初始化"""
        Server.init_app()
        # screen.set_ori_change_listener(self.on_ori_change)

    def on_ori_change(self, w, h):
        if w != Utils.sys_info["screen_w"]:
            if w > h:
                Utils.sys_info["vertical"] = False
            else:
                Utils.sys_info["vertical"] = True
            Utils.sys_info["screen_change"] = True
            Utils.sys_info["screen_w"] = w
            Utils.sys_info["screen_h"] = h

    def tunnel(self, k, v):
        # print(f"js消息通道：{k} {v}")

        if k == "mounted":
            self.get_config(v)
        if k == "start":
            self.start(v)
        if k == "stop":
            self.stop()
        if k == "tip_mounted":
            self.tip_fun_name = v
            Server.tip_fun_name = v

    def start(self, config):
        Server.config = Utils.json_to_dict(config)
        Server.init_config()
        Server.init_cache()
        Utils.save_json("config", Server.config)
        Utils.save_json("cache", Server.cache)
        self.run()

    def run(self):
        if Utils.sys_info["screen_w"] < Utils.sys_info["screen_h"]:
            Utils.eval_js(self.Win, "toast", "请横屏使用！")
            return False
        if "total_hz" in Server.cache and Server.cache["total_hz"] >= 12:
            Utils.eval_js(
                self.Win, "toast", "恭喜发财！今天大丰收(已偷满12个环状)，明天再来吧！"
            )
            return False
        res = Server.switch_scene(self.Win)
        if res:
            self.Win.close()
            self.is_win_close = True
            self.open_tip_win()
            Utils.randomSleep(1)
            self.run_scene()

    def run_scene(self):
        print(f"运行场景：{Server.active_scene}")
        if Server.active_scene["id"] in self.sceneDict:
            Server.active_scene["start_time"] = time.time()
            self.sceneDict[Server.active_scene["id"]]()

    def get_config(self, fun_name):
        Utils.eval_js(self.Win, fun_name, Server.config)

    def stop(self):
        self.Win.close()
        Utils.app_exit()

    def open_main_win(self):
        ui_path = R.ui("index.html")
        if Server.config["dev"]:
            ui_path = Server.config["dev_serve"]
        w = WebWindow(ui_path)
        w.tunner(self.tunnel)
        w.size('90vw', '90vh')
        w.background("#00000000")
        w.show()
        self.Win = w

        while True:
            if not self.is_win_close:
                if Utils.sys_info["screen_change"]:
                    if Utils.sys_info["vertical"]:
                        w.size('91vw', '91vh')
                    else:
                        w.size('89vw', '89vh')
                    Utils.sys_info["screen_change"] = False
            else:
                break
            Utils.randomSleep(1)

    def open_tip_win(self):
        ui_path = R.ui("index.html#/tip")
        if Server.config["dev"]:
            ui_path = Server.config["dev_serve"] + "#/tip"
        w = WebWindow(ui_path)
        w.tunner(self.tunnel)
        w.mode(2)
        w.dim_amount(0)
        w.size("800", "300")
        w.background("#00000000")
        w.gravity(80 | 3)
        w.show()
        self.Tip_win = w
        Server.tip_w = w
