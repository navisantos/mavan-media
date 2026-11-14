#!/usr/bin/env bash
# Coloca a capa nos primeiros N frames do vídeo (o TikTok usa o primeiro frame como capa).
# O áudio é atrasado em N/30 s para continuar sincronizado.
# N padrão = 3 (Instagram). Para o vídeo do TikTok use 30 (1 segundo inteiro de capa).
# Uso: tools/add_cover_frames.sh capa.png video_original.mp4 video_saida.mp4 [N_frames]
set -euo pipefail
capa="$1"; entrada="$2"; saida="$3"; n="${4:-3}"
atraso=$(( n * 1000 / 30 ))
ffmpeg -y -loglevel error -framerate 30 -i "$capa" -i "$entrada" -filter_complex \
 "[0:v]scale=1080:1920,format=yuv420p,loop=loop=$((n-1)):size=1:start=0,trim=end_frame=$n,setpts=PTS-STARTPTS[c];[1:v]format=yuv420p,setpts=PTS-STARTPTS[v];[c][v]concat=n=2:v=1:a=0[vv];[1:a]adelay=${atraso}|${atraso}[a]" \
 -map "[vv]" -map "[a]" -r 30 -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -f mp4 "$saida.tmp.mp4"
mv "$saida.tmp.mp4" "$saida"
