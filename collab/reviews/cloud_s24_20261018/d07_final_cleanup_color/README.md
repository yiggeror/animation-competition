# S24 F024最终清边＋分区色门候选

**唯一取图：[F024_final_rgba.png](candidates/F024_final_rgba.png)**，SHA256 `44137d740ac5d07ca0258019c28cdf8f9b648d77ba79eda07f366f24503753db`。固定源4a203f2，零新生图。Astra此前双审通过的主体/转态保留，本轮完成已授权残边清理和色门，**待Astra终锁，不先开032**。

[灰底全图](qa/F024_final_gray_full.jpg)、[深底脸耳颈](qa/F024_final_dark_face_ear_neck.jpg)、[袖口8倍](qa/F024_final_dark_cuff8x.jpg)、[原母/4a203/最终三图](qa/master_source_final_actual.jpg)已实看。抬颏、提眉、闭口笑、发根/整头/颈与完整泡袖沿4a203，无新姿势或新生成。

**真实残边清理：**按[授权](provenance/authorization.md)的两处native坐标，使用完整袖口→裸臂走廊；008原上臂沿已交仿射作原像素供体，先独立提取其上臂alpha，防止源衣黄进入空隙。右侧只替裸臂RGB、alpha不改；左侧完整清理旧半透明边，保真实前臂轮廓与荷叶颜色/描线/AA。[灰/深底前后](qa/cleanup_dark_before_after.jpg)、[走廊及源mask](masks/)、[清理核](qa/cleanup_validation.json)、[残边专项核](qa/residual_edge_validation.json)齐。共773像素变化、456个alpha变化且仅左走廊；源头颈耳发/胸部0变化，真荷叶保护域0变化。右露臂旧线暗像素21→0，左旧空隙残影12→0。不是把含真实折线的整个坐标框全抹掉。

**分区色修：**锁母0485c6fe为唯一色参照，冠发/近尾/远尾各自独立材质域；脸、耳、颈各分受光/暗面，共9分区。RGB小偏移保留原渐变，发部深线/脊线/高光、眉眼/鼻嘴/腮红及领口AA锁住；皮肤明暗软过渡，不改黄衣、白领白点，不做全图均值拉。[源与锁母独立语义样点](qa/independent_source_master_sample_locations.jpg)、[全部mask与weight](masks/)、[数值与完整阈值定义](qa/color_validation.json)保全。皮肤对两图均按alpha≥248、颜料R≥235、材质域内≥3px取对应明暗内区，排除线/AA混色和腮红；样点按修前值冻结，修后不重分组。色门是对应材质内部样点的均值/中位数±4，不冒称不同视角所有皮肤像素全图均值一致。

| 分区 | 减RGB | 修后均值ΔRGB对锁母 |
|---|---|---|
| crown | (9.0, 5.0, 4.0) | (3.87796, 2.63174, 1.56129) |
| near_tail | (6.0, 3.0, 3.0) | (2.92662, 1.64999, 0.41199) |
| far_tail | (7.0, 5.0, 4.0) | (1.44602, 0.00439, -0.57652) |
| skin_face_lit | (0.0, 5.0, 6.0) | (0.01339, -0.21958, 0.39235) |
| skin_face_shadow | (0.0, -2.0, 1.0) | (0.62065, 1.19629, 0.32331) |
| skin_ear_lit | (0.0, 6.0, 7.0) | (0.00765, -0.74102, -0.23536) |
| skin_ear_shadow | (2.0, 3.0, 6.0) | (0.43924, 1.17305, 0.83005) |
| skin_neck_lit | (-1.0, 5.0, 5.0) | (0.92045, -0.61185, 0.65131) |
| skin_neck_shadow | (2.0, 4.0, 5.0) | (0.40358, -0.45836, -0.3671) |

九区最大通道均值差3.87796，全部均值/中位数在±4。**色修步骤alpha变化0**、发线/高光0、表情/腮红0、独立冻结领片0、衣黄/白0、材质域外0，1100行以下全体0变化。源4a203→最终的alpha差仅上述左收口456像素，[两步骤保护核](qa/combined_protection_validation.json)分开列，未把裸臂AA或透明底RGB误当白布。真正衣料/荷叶保护未被清理或校色覆盖。

[灰底13帧](qa/S24_final_F019_031_gray_13f_24fps_NOT_SCENE.mp4)、[深底13帧](qa/S24_final_F019_031_dark_13f_24fps_NOT_SCENE.mp4)及[实际解码接触表](qa/actual_decoded_gray_dark_13f_contact.jpg)：019×5→024×8，场景019–031，B整层`.70+(590,20)`，1920×1080/24fps/无声；0/4/5/12实际跳点及[编码核](qa/exposure_validation.json)齐。已实际打开灰深底接触表、全图与放大连接部看，未见旧残线或明显材质跳。中性人物层曝光不冒称Canvas接景、完整60f或音轨验收；Astra原速主观终审仍待。

源008/009、原4a203候选、锁母、019及所有完整原prompt/response原路径保留，[固定源SHA](provenance/fixed_sources.json)逐Git原件核；本轮0图像调用、0新prompt。复现依次运行本目录`tools/cleanup_corridor.py`、`tools/color_regions.py`、`tools/build_exposure.py`，必要时独立跑`tools/verify_protection.py`。只交独占目录，不改共享分支、实现、留言、声音、EDL或ready。
