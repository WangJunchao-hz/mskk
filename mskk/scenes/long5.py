import time

from ..server import Server

# 导入工具类
from ..utils import Utils


class Long5:
    def __init__(self):
        """实例初始化"""
        pass

    def initScene(self):
        """初始化场景"""
        Server.push_log(log="前往龙窟五层中...")
        while True:
            local = Server.get_location()
            if local:
                if any(k in local for k in ["长", "安", "城"]):
                    self.chang_an_chen()
                elif any(k in local for k in ["傲", "来", "国"]):
                    self.ao_lai_map()
                elif any(k in local for k in ["花", "果", "山"]):
                    self.hua_guo_shan_map()
                elif any(k in local for k in ["北", "俱", "芦","洲"]):
                    self.bei_ju_lu_zhou_map()
                elif "龙" in local and "一" in local:
                    self.long_ku1_map()
                elif "龙" in local and "二" in local:
                    self.long_ku2_map()
                elif "龙" in local and "三" in local:
                    self.long_ku3_map()
                elif "龙" in local and "四" in local:
                    self.long_ku4_map()
                elif "龙" in local and "五" in local:
                    self.long_ku5_map()
                else:
                    Server.handle_exc()
            else:
                Server.handle_exc()

    def chang_an_chen(self):
        """长安城场景"""
        res = Server.go_to_init_Map("fxf_al")
        if res:
            Utils.randomSleep(3)
            self.ao_lai_map()
        else:
            Server.handle_exc()

    def ao_lai_map(self):
        """傲来国场景"""
        # 到了傲来先吃摄妖香
        res = Server.use_syx()
        if res:
            # 过图时到达指定位置后动作
            def cb():
                # 传送去花果山
                hasCS = Utils.click_by_rect("g_chuan_song")
                if hasCS:
                    return True
                else:
                    return False

            flag = Server.guo_map("map_hgs", cb)
            if flag:
                Utils.randomSleep(3)
                self.hua_guo_shan_map()
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def hua_guo_shan_map(self):
        """花果山场景"""
        res = Server.use_syx()
        if res:
            def cb():
                # 只显示npc，需要点击屏蔽
                Utils.click_by_rect("g_pb_rect")
                Utils.randomSleep(1)
                if "pb_full_tw_is_click" not in Server.cache or not Server.cache["pb_full_tw_is_click"]:
                    Utils.click_by_rect("g_pb_full_tw_rect")
                    Server.cache["pb_full_tw_is_click"] = True
                    Utils.save_json('cache', Server.cache)
                    Utils.randomSleep(1)
                # 去找npc
                npc = Server.get_pos_while("bjlz_npc",i=3,handle_exc=False)
                if npc:
                    Utils.click_by_pos(npc)
                    Utils.randomSleep(1)
                    is_npc = Server.get_pos_while("bjlz_npc_flag",i=3,handle_exc=False)
                    if is_npc:
                        Utils.click_by_pos(is_npc)
                        return True
                    else:
                        return False
                else:
                    return False
            flag = Server.guo_map("map_bjlz", cb)
            if flag:
                Utils.randomSleep(3)
                self.bei_ju_lu_zhou_map()
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def bei_ju_lu_zhou_map(self):
        """北俱芦洲场景"""
        res = Server.use_syx()
        if res:
            # 到了北俱芦洲需要解除屏蔽
            is_pb = Server.get_pos_while("g_pb_back",i=3,handle_exc=False)
            if is_pb:
                Utils.click_by_pos(is_pb)
                Utils.randomSleep(1)
            flag = self.long_ku_map(1)
            if flag:
                Utils.randomSleep(3)
                self.long_ku1_map()
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def long_ku_map(self, num):
        """龙窟场景 1-5层"""
        def cb():
            hasCS = Utils.click_by_rect("g_chuan_song")
            if hasCS:
                return True
            else:
                return False
        return Server.guo_map(f"map_lk{num}", cb)

    def long_ku1_map(self):
        res = Server.use_syx()
        if res:
            flag = self.long_ku_map(2)
            if flag:
                Utils.randomSleep(3)
                self.long_ku2_map()
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def long_ku2_map(self):
        res = Server.use_syx()
        if res:
            flag = self.long_ku_map(3)
            if flag:
                Utils.randomSleep(3)
                self.long_ku3_map()
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def long_ku3_map(self):
        res = Server.use_syx()
        if res:
            flag = self.long_ku_map(4)
            if flag:
                Utils.randomSleep(3)
                self.long_ku4_map()
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def long_ku4_map(self):
        res = Server.use_syx()
        if res:
            flag = self.long_ku_map(5)
            if flag:
                Utils.randomSleep(3)
                self.long_ku5_map(True)
            else:
                Server.handle_exc()
        else:
            Server.handle_exc()

    def long_ku5_map(self, use=False):
        Server.push_log(log="到达龙窟五层开始偷卡")
        if use:
            # 先解除摄妖香
            Server.use_dao_ju_by_img("dao_ju_dmc")
            Server.cache['last_use_syx']['expire'] = True
            Utils.save_json('cache', Server.cache)
            # 使用后关闭背包
            Server.close_dao_ju(False)
            Utils.randomSleep(1)
        Server.start_tou_ka()
        return False

        # 如果在战斗继续战斗
        # operate.check_is_fired()

        if not Utils.dao_ju_datas:
            # 初始化背包数据
            operate.init_bei_bao()

        # 跑图并且战斗
        def run_and_fire(is_run=True):
            can = Utils.get_qx_status()
            if not can:
                # 需要补充状态
                operate.bu_xue()
            if is_run:
                # 随机遇怪
                operate.randow_run_map("map_long5_rect")
            lasPos = None
            while True:
                # 检测是否遇到怪了
                rs = operate.check_is_fired()
                if rs:
                    print(f"战斗结束了{rs},清点战绩")
                    operate.check_bei_bao()
                    # if rs == 3:
                    #     # 需要补血

                    #     operate.bu_xue()
                    break
                else:
                    # 检测是否停止了
                    txt = Utils.getTxtByTpl("map_rect")
                    if txt:
                        if lasPos == txt[0].text:
                            print("停止移动了")
                            break
                        else:
                            # print("移动中...")
                            lasPos = txt[0].text
                Utils.randomSleep(1)

        while True:
            if Operate.currentScene["stop"]:
                print(
                    f'{Operate.currentScene["name"]}场景偷完了或是时间到了，需要切换场景'
                )
                is_success = Operate.switch_scene()
                if is_success:
                    # 停止当前场景
                    break
                else:
                    # 重新启动
                    Operate.currentScene["stop"] = False
                    Operate.currentScene["start_time"] = time.time()
            else:
                # 检测人物是否挂了
                isLive = operate.check_is_live()
                if isLive:
                    print("随机移动遇怪偷卡")
                    run_and_fire()
                else:
                    self.startScene()
                    break
            Utils.randomSleep(1)
