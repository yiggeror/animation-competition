# S08 first49

入口 s08_first49_scene.js，1920×1080、24fps、49/24秒。基线837f8ab8fb02f3a013f11a9e204b6db3a56d3491，仅新增046×3（46–48）；049+所有入口拒绝。

046母7722c85545660ae240acc72d512985572b1a5ba5532780b150b4b8274c385ec2及三层SHA已核，RGBA重建0差、互斥；旧45PNG逐字节相同。旧46合同184子帧/46帧绘制及全部scene/light/glow/emit源码回归。场景、曝光、火曲线、原冷蓝底、低杆/罩高/盒1665及接影均沿原值。

药头(1350,782.572972972973)，木出口(1310.442494558651,806.8258854425643)，相对043真手柴(-65,-12)。原芯顶(1415,794.572972972973)，emit保原+2。046–048芯火公式/输出数值见WICK_WITHDRAWAL_046_048.json；近手柴在侧管前。

## 只渲新增3帧

```sh
node tools/js/frames.cjs collab/reviews/20261019_0040_s08_first49_scene/s08_first49_scene.js build/S08_first49_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.9166666666666667 --to 2.0416666666666665
```

输出00046.png–00048.png。原00000–00045从07966095db7028677e884702cc784e69c172d0f2的cloud_s13_20261018/render_assist/s08_first46按SHA复用，无需重渲。原first46实际MP4 SHA f0963b0206d608714a44c9cfc122d71089872affba7faab875add6c14cc49eea。

新增真实门：045→046撤柴后，芯火须在固定芯顶独立可见，match继续随药头；检查两火自然、侧管前景、低杆座、单盒接影。043–045同根两火合并，未单独签独立芯焰；非零数值不能替代这次Canvas门。本包新实际Canvas0帧。

RUNTIME_ROWS共51项：3新JS、3新046PNG、45旧blob。作者同批046层可同blob去重。npm test及python verify_F046.py /path/to/astra_s08_first_mother_20261018_1433为静态/命令/像素校验。
