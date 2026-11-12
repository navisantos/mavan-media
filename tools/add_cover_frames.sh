#!/usr/bin/env bash
# Coloca a capa nos 3 primeiros frames do vídeo (o TikTok usa o primeiro frame como capa).
# O áudio é atrasado em 0,1 s (3 frames) para continuar sincronizado.
# Uso: tools/add_cover_frames.sh capa.png video_original.mp4 video_saida.mp4
set -euo pipefail
capa="$1"; entrada="$2"; saida="$3"
ffmpeg -y -loglevel error -framerate 30 -i "$capa" -i "$entrada" -filter_complex \
 "[0:v]scale=1080:1920,format=yuv420p,loop=loop=2:size=1:start=0,trim=end_frame=3,setpts=PTS-STARTPTS[c];[1:v]format=yuv420p,setpts=PTS-STARTPTS[v];[c][v]concat=n=2:v=1:a=0[vv];[1:a]adelay=100|100[a]" \
 -map "[vv]" -map "[a]" -r 30 -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -f mp4 "$saida.tmp.mp4"
mv "$saida.tmp.mp4" "$saida"
