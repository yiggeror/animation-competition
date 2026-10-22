#!/bin/bash
# 合作方渲不了画面（他们的环境开不了 Chromium）：这个脚本每 3 分钟拉一次分支，
# 看到 js/anim/sXX.js 有新提交，就把改过的镜头渲成 1280×720 清版小片和接触表，放进 collab/reviews/auto_render/<提交>/ 推回去。
# 用法：nohup tools/auto_render.sh > build/auto_render.log 2>&1 &
cd "$(dirname "$0")/.." || exit 1
B=claude/intelligent-euler-t2so6e
last=${1:-$(git rev-parse HEAD)}   # 可传起点提交（补渲漏掉的镜头）
while true; do
  sleep 180
  git fetch -q origin $B 2>/dev/null || continue
  head=$(git rev-parse origin/$B)
  [ "$head" = "$last" ] && continue
  git pull -q --rebase --autostash origin $B || { echo "$(date -u +%H:%M) pull 失败"; continue; }
  src=$(git rev-parse HEAD)                     # 这一轮实际渲的源提交；渲完只把基线推进到这里，渲染期间新到的提交下一轮再渲（Astra 指出的并发漏镜）
  changed=$(git diff --name-only $last $src -- 'js/anim/s*.js' | sed -n 's#^js/anim/\(s[0-9a-z]*\)\.js$#\1#p' | sort -u)
  [ -z "$changed" ] && { last=$src; continue; }
  out=collab/reviews/auto_render/$(git rev-parse --short $src); mkdir -p $out
  for s in $changed; do
    id=$(echo $s | tr a-z A-Z); rm -rf build/auto_render/$id
    if timeout 2400 node tools/js/frames.cjs js/anim/$s.js build/auto_render/$id --fps 24 --w 1280 --h 720 --workers 4 --mp4 $out/$id.mp4 > $out/$id.log 2>&1; then
      ffmpeg -loglevel error -y -i $out/$id.mp4 -vf "fps=6,scale=320:-1,tile=6x6" -frames:v 1 $out/${id}_contact.jpg
      ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $out/$id.mp4 > $out/$id.frames
      sha256sum $out/$id.mp4 >> $out/SHA256SUMS.txt; rm -f $out/$id.log
    else echo "$id 渲染失败，见 $id.log"; fi
  done
  git add $out && git commit -qm "collab: 自动渲染 $(echo $changed | tr '\n' ' ')（源 $(git rev-parse --short $src)）" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018izVeBsCAWYGJUmZwpX2YC" -- $out && git pull -q --rebase origin $B && git push -q origin $B
  last=$src
  echo "$(date -u +%H:%M) 渲了 $(echo $changed) → $out"
done
