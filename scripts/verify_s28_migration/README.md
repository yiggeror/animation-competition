# S28 纯改址迁移六帧门

前提：原 4aa566ae 完整 192 帧已实看通过；七份文字候选及36原blob资产已统一迁入生产。此目录两文件应放 `scripts/verify_s28_migration/`，从仓库根执行：

```sh
python3 -m http.server 8198 --bind 127.0.0.1 >/tmp/s28-production-http.log 2>&1 &
S28_HTTP_PID=$!
S28_OUTPUT_DIR=/tmp/s28-production-six node scripts/verify_s28_migration/verify_six.cjs
S28_STATUS=$?
kill "$S28_HTTP_PID"
exit "$S28_STATUS"
```

先核64个运行文件精确blob、原入口转导出文本、原曝光/192路由；再逐帧实际出000/012/042/132/162/191，与2051e3fa原始PNG SHA比较。只在六张全字节相同且原整片通过时，允许以等价改址继承整片门。任何源码/依赖/绑定或实PNG不同都失败并扩大实际验证，不能预判等价。当前仅语法检查，未运行迁移浏览器。
