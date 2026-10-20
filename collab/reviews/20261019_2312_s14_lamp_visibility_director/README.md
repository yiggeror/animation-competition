# S14 lamp visibility decision

## 2026-10-19 23:12 UTC · S14 既有挂灯段的可见性，请导演作一次最小机位决定

S14 已批准的 G096–131（4.0–5.5秒）是从箱顶握真实提梁、提灯、低钩承重后放手；全镜10秒和5.5秒幕亮保持。两夹固定布的095已锁，独立小满末段继续制作。

我们实核了原 layout.py 和正式 S15 渲染，二者幕底/幕高与坐标原点不同，不能直接混用数值。以已过 S15 的真实光源 S.lamp=(1.52,0.70,1.30) 为接续基准，灯在幕后；当前候选提梁至相机的视线穿过幕内，握环、落钩与松手看不见。只向幕侧移动一个点也不能保证完整手环可见，更不能为此搬动 S15 光源而改变已过皮影。

建议：保 S15 光源/幕与同一 S08 红灯外形，在既有096–131的1.5秒内允许一个看清手、提梁、预先系好的低钩的局部机位，随后按原5.5秒幕亮继续。是否同意？若必须全程原全景，请明确接受哪项最小空间调整；我们不先挪灯或重做已过 S15。

实际零调用图/来源在 `collab/reviews/20261019_2312_s14_lamp_visibility_director`：S14_S15_LAMP_COORDINATES_OCCLUSION_THIN.jpg 与五拍完整体量图。前者是视线遮挡计算，后者只判动作可达，均不是正式接景或已冻结新镜头。红灯诊断高0.349m与提梁尺寸仍是尺度候选，S15只锁真实火光源，并未锁这只程序灯体；没有把旧坐标差或条件性影移冒称既有成片错误。

## Evidence integrity
- S14_S15_LAMP_COORDINATES_OCCLUSION_THIN.jpg SHA256 c883ab8da9fa8f455c8e03200602a095233872523d01953cd493caba193c5f99
- S14_S15_LAMP_COORDINATES_OCCLUSION_THIN.json SHA256 dd57fc059637934ae2492ad670c01181c574ab7f90e35897d1cc1ac8b3f394a0
- G096_G131_FIVE_COMPLETE_VOLUME_ZERO_CALL_REVIEW.jpg SHA256 5b257da4a9997fa5f91f6b106d92ca6be1b93e073df2beb0d9df21cbc7ed9fe9
- G096_G131_FIVE_COMPLETE_VOLUME_ZERO_CALL.json SHA256 5633668640d74310a09b6fd9d19551a69a4576660e27c67ce2727b194d191eb5
- S15_OPTICAL_ORIGIN_ADDITIONAL_SOURCE_THIN.json SHA256 08b3624f5cd5c202d85e2ec544aac027397f188b0e5a7b8317d33fdebfe1b1a4

0 generation calls, no production/light/camera edits. Main reviewer actually inspected both diagrams before publication. Independent X197–208 arm-closing inputs are proceeding separately.
