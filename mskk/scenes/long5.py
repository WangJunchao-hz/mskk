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
        while True:
            local = Server.get_location()
            if local:
                if "长" in local:
                    self.chang_an_chen()
                else:
                    Server.handle_exc()
            else:
                Server.handle_exc()

    def chang_an_chen(self):
        """长安城场景"""
        res = Server.go_to_init_Map("fxf_al")
        if res:
            self.ao_lai_map()

    def ao_lai_map(self):
        """傲来国场景"""
        Utils.randomSleep(10)
        return False
        local = operate.getLocation()
        if "长" in local:
            self.startScene()
        # 到了傲来先吃摄妖香
        operate.useDaoJuByImg("dao_ju_syx")
        # 使用后关闭背包
        operate.closeDaoju(False)
        # 1-3秒后打开地图
        Utils.randomSleep(1)

        # 过图时到达指定位置后动作
        def cb(i=1):
            # 传送去花果山
            hasCS = Utils.clickByTpl("chuan_song", need_stop=False)
            if hasCS:
                return True
            else:
                return False

        operate.guo_map("map_hgs", cb)
        Utils.randomSleep(3)
        self.hua_guo_shan_map()

    def hua_guo_shan_map(self):
        """花果山场景"""
        local = operate.getLocation()
        if "傲" in local:
            self.ao_lai_map()

        def cb(i=1):
            if i == 1:
                # 只显示npc，需要点击屏蔽
                Utils.clickByTpl("pb_rect")
                Utils.randomSleep(2)
                if not Utils.operate_cache["pb_full_tw_is_click"]:
                    Utils.clickByTpl("pb_full_tw_rect")
                    Utils.operate_cache["pb_full_tw_is_click"] = True
                    Utils.randomSleep(1)

            # 去找npc
            hasCS = Utils.clickByTpl("bjlz_npc", i=10, sleep=1)
            if hasCS:
                Utils.randomSleep(1)
                hasNpc = Utils.getPos("bjlz_npc_flag")
                if hasNpc:
                    Utils.clickByPos(hasNpc)
                    return True
                else:
                    return False
            else:
                return False

        operate.guo_map("map_bjlz", cb)
        Utils.randomSleep(3)
        self.bei_ju_lu_zhou_map()

    def bei_ju_lu_zhou_map(self):
        """北俱芦洲场景"""
        local = operate.getLocation()
        if "花" in local:
            self.hua_guo_shan_map()

        # 到了北俱芦洲需要解除屏蔽
        hasPB = Utils.getPos("g_pb_back", i=2)
        if hasPB:
            Utils.clickByPos(hasPB)
        Utils.randomSleep(1)
        self.long_ku_map(1)
        Utils.randomSleep(3)
        self.long_ku1_map()

    def long_ku_map(self, num):
        """龙窟场景 1-5层"""

        def cb(i=1):
            hasCS = Utils.clickByTpl("chuan_song", need_stop=False)
            if hasCS:
                return True
            else:
                return False

        operate.guo_map(f"map_lk{num}", cb)

    def long_ku1_map(self):
        local = operate.getLocation()
        if "北" in local:
            self.bei_ju_lu_zhou_map()
        self.long_ku_map(2)
        Utils.randomSleep(3)
        self.long_ku2_map()

    def long_ku2_map(self):
        local = operate.getLocation()
        if "龙" in local and "一" in local:
            self.long_ku1_map()
        self.long_ku_map(3)
        Utils.randomSleep(3)
        self.long_ku3_map()

    def long_ku3_map(self):
        local = operate.getLocation()
        if "龙" in local and "二" in local:
            self.long_ku2_map()
        self.long_ku_map(4)
        Utils.randomSleep(3)
        self.long_ku4_map()

    def long_ku4_map(self):
        local = operate.getLocation()
        if "龙" in local and "三" in local:
            self.long_ku3_map()
        self.long_ku_map(5)
        Utils.randomSleep(3)
        self.long_ku5_map(True)

    def long_ku5_map(self, use=False):
        local = operate.getLocation()
        if "龙" in local and "四" in local:
            self.long_ku4_map()
        if use:
            # 先解除摄妖香
            operate.useDaoJuByImg("dao_ju_dmc")
            # 使用后关闭背包
            operate.closeDaoju(False)
            Utils.randomSleep(1)

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
