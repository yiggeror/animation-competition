# S07 F062 单张真实绘制候选，待 Astra 锁定

本轮已核调用状态后，只提交一次原生图像请求，成功取得一份真实原件。新裤体从腰臀到双腿、膝后转面和两裤口连续；切膝口、尖楔及旧碎片已清除。068/073尚未生成，不以本单张静态通过代替完整步态或整镜验收。

唯一交审图为 [F062完整透明候选](candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png)，SHA256 `393622a77349083751122520b690bd35017f8535a25560d8cca775446d2eeb2f`；人物源画布1672×1080。原有注册不变：s=0.36410361842105265，t=(627.0254537171638,402.7604324894813)。可直接看 [057→062同注册实际对照](qa/F057_F062_registered_actual_support_comparison.png)、[最后腰口深底对照](qa/waist_internal_source_underlay_before_after_dark.png)及[最终完整灰底](qa/F062_chosen_final_full_gray.png)。另附 [世界画布透明图](candidate/F062_world_registered_PENDING.png)，1672×941。

近鞋和裸踝保持原图层、原位置、原比例与颜色，真实alpha128鞋底仍为774.874330515797world；近鞋不透明核心RGBA变化0。头衣保留原节拍；原头衣、完整双臂、真手与玉镯均保留源材质图层。远鞋原层位于新裤层下，近鞋位于上层，隐藏远鞋不再顶掉前景裤。腰口原衣缘AA叠在完整新裤底层上，透明保护扩边不再阻挡裤料，近踝灰缝与远踝旧三角已消除。近裤左外793/926的一线浅弧已追溯为057同一真远鞋后跟，保留原归属，未当作旧裤渣误抠。

实际采用的是原生输出的完整裤体及其真实黑线、褶影和邻接AA，没有用代码绘制人物或做分肢变形。已批470×780裁片左右只各加25透明列，未改画内坐标，工具返回1024×1536，整块统一0.5078125缩至520×780后去掉透明补边，贴回(650,280)。完整裤层3946px位于旧技术罩外，含新轮廓及合法底层覆盖，显式源材质mask随包；这是整裤语义采用范围，未夹带新手影、重复鞋或外围低alpha光晕。生成的裤料原色比057偏亮，故仅对新navy材质作(−6,−5,−5)校正，深墨线和全部alpha不动，原生褶影保留。最终裤料均色差RGB为(+0.129,−0.222,−0.461)，符合±4门。

透明AA与遮挡按真实图层合成：保留源材质RGBA，允许最终扁平图的接边像素因其新底层而变化；不把扁平AA字节锁当成材质保护。源身体与鞋的可见不透明核心仍逐RGBA相同。图层、真实mask与统计见 [production_layers](production_layers/)、[层次检查](qa/layered_final_checks.json)和[颜色门](qa/final_trousers_palette_gate.json)。

调用与来源完整保全：输入门为 `10908f920bec7989b78558c1b248f93acae2e087`；实际 [原始PNG](originals/F062_call01_raw.png) SHA `efa81720135228ccec5c7af65b05d75a8ec2db39b28c2dd1d6ba740ad89722b0`，[完整提示词](requests/prompt.txt)、[实际参数](requests/arguments.json)、[输入冻结](requests/input_freeze.json)、[原始工具返回](requests/raw_return.json)及[执行状态](requests/execution_state.json)齐。原返回base64、工具宿主PNG和归档PNG逐字节相同。F062计数为1次请求／1份原件；后处理新增调用0。

`candidate/F062_native_art_exact_approved_mask_PENDING.png`、`F062_complete_native_trousers_semantic_PENDING.png`、`F062_layered_before_waist_source_extension_NOT_APPROVED.png` 和 `F062_complete_native_layered_color_locked_PENDING.png` 均是保全的未通过采用诊断，勿取用。先沿同原件补全484px真实腰口上缘材质，扁平图460px变化全部位于y<530，见 [腰口取层补全](qa/upper_waist_source_extension_checks.json)。此后仍有封闭18px内部孔，其同坐标native是蓝衫遮挡而无navy。没有把蓝料冒称navy或重新生图：仅将同一已校色native裤层紧邻下方4原生行的真实RGBA取为隐蔽底层，18孔加原衣AA下9px，共27px逐点源映射，原衣层与人物外轮廓不改，见 [完整映射与检查](qa/internal_waist_native_source_underlay_checks.json)。这27px局部真实材质延接明确保全，不称全图所有位置均为同坐标native。

最终重放顺序：`python align_and_adopt.py` → `python compose_complete_native_layers.py` → `python close_internal_waist_from_native_source.py` → `python register_and_support.py`。独立临时目录从同一raw与已提交10908/e3d源重放，最终PNG、世界注册PNG及生产图层SHA全部相同，见 [重放结果](qa/isolated_final_replay_checks.json)。

作者与6.1sol的当前有限静态复核通过，见 [最终独审记录](qa/independent_61sol_layered_final_PASS.json)。27点供体映射与正常图层合成已独立逐RGBA重放，无剩余本次静态阻断。此结论不代 Astra 锁母。

本包仅交062成态及静态形体、接地和裤色门，不含实景、音轨或动态播放结论，不登记ready。
