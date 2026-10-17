# 相对路径和接入范围

小满可供Opus试渲：把xiaoman/probe/assets/chars下33文件复制到仓库assets/chars；把xiaoman/probe/assets/flips/x01_prone_phone.flip.json复制到assets/flips/x01_prone_phone.flip.json。只影响S01，S04独立表不动。运行python3 -I tools/flip_manifest.py x01_prone_phone 288，应exit0；本包已实际校验。重点看k14转脚/鞋扣，以及回程重用桥是否生硬，不仅看静态对齐。

奶奶partial/assets/chars为15个可复用静态状态，未附完整flip，暂不替换g01_beans.flip.json。原件含失败态，失败态不进入partial目录。末豆残留+3.07px越线的c05b不能使用。

请先看奶奶实际手部图再共同定下一次修正：c04b持荚底与成功c06b的两腔空壳形状可组成两个真实参考，明确移除左侧凸豆；这不同于继续单底全文盲抽。本包本身不发起额外生成。抬头/眨眼是否可复用旧图须实际检查荚与手形连续性。
