# 参考复现（从仓库根目录）

固定本包source_manifest对应源和字体/Pillow/NumPy/SciPy。所有输出只写本review目录。

```sh
python collab/reviews/cloud_s12_20261018/tools/build_geometry.py
python collab/reviews/cloud_s12_20261018/tools/build_reference.py
python collab/reviews/cloud_s12_20261018/tools/verify_reference.py
python collab/reviews/cloud_s12_20261018/tools/check_support_camera.py
```

code_crane_points.json和三张code_prop原件已保留，可直接复现构造。若需从源码重取代码道具，先运行extract_existing_code_prop.cjs；它仅用本地现有makeCrane/solve/drawPuppet，不生成人物、不调用生图模型、不渲正式场景。手型体块只给掌握/杆遮挡关系，不能代替原生五指审查。包的接口文档补充字段不由构造工具重新生成；不要将重跑工具当Astra冻结批准。
