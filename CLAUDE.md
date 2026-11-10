# Mavan 3D: vídeos e publicação (contexto do projeto)

Este arquivo guarda o contexto do projeto para qualquer sessão futura do Claude. Leia antes de produzir ou publicar qualquer coisa.

## Quem e o quê
- Marca: Mavan 3D (@mavan.3d), produtos impressos em 3D. Dono: Ivan (São Paulo). Mariana revisa roteiros e legendas.
- Conteúdo: vídeos verticais 2D animados (1080x1920, 30 fps) para Instagram Reels e TikTok. Personagens: **Mari** (a marca; olhos verdes, sem óculos, avental com coração) e o **cliente** cético (sarcástico).
- Dois públicos, alternados: **C** = comunidade 3D (dicas, bastidores) e **B** = cliente final que quer brinde personalizado. Os vídeos B de novembro/dezembro focam em **Natal**, com itens que a pessoa ainda personaliza (nome da marca, foto da família, ano, pintura).
- Tom: casual, em português do Brasil. O Ivan chama o Claude de "champs"/"capitão".

## Regras de conteúdo
- **Capa sempre com um pouco do tema do vídeo** (ex.: gorro de Natal na Mari e bolas penduradas). Não reaproveitar capa genérica.
- Roteiro e legendas são da Mariana: o Claude propõe, ela edita no portal. Nunca alterar o texto que ela revisou.
- Só publica o que estiver com a flag **Liberado para publicar** marcada no portal.
- Números e fatos de custo vêm do Ivan (ex.: filamento R$ 100/kg, falha ~20%); energia calculada com 105 W (Bambu P1S/X1C em PLA) e tarifa Enel SP com impostos ~R$ 0,98/kWh. Peças de exemplo devem ser rotuladas como ilustrativas.
- Os itens de Natal que a Mavan faz: enfeite com nome da marca + espaço para foto, enfeite com ano gravado, etiqueta de presente que vira enfeite, kit para pintar em casa. Prazo de produção cerca de 1 semana; pedir cedo.

## Fluxo de produção de um vídeo
1. Roteiro aprovado no portal (flag marcada).
2. Vozes na ElevenLabs (modelo `eleven_v4`, tags como `[sarcastic]`, `[explaining]`): voz **Sofia** `n2a9VtkZLl8j1FSXHsL7` para a Mari e **Luciano** `FOhTvAmqIK234DPck9zT` para o cliente. Gera 1 take por fala (cada take custa ~60–140 créditos). Nunca repetir a chamada de geração para "tentar de novo". Escrever números e siglas por extenso na fala ("três D").
3. Baixar os áudios (o domínio `elevenlabsusercontent.com` precisa estar liberado nas configurações do Claude), converter para WAV mono 44,1 kHz em `tools/aud*/fin/NN.wav`.
4. Copiar `tools/gen_natal_enfeites.py` (modelo mais recente), trocar `LINES`, `TITLES`, as funções de cena e o texto das pílulas finais. `python3 -I gen.py preview` gera um mosaico para conferir; `python3 -I gen.py render` gera o MP4 (~45 s de render).
5. Capa: copiar `tools/cover_natal.py` e adaptar texto, chips e elementos do tema.
6. Mandar vídeo e capa para o Ivan aprovar.
7. Aprovado: copiar para `reels/AAAA-MM-DD-slug/video.mp4` e `capa.png`, `git push`, e preencher no portal os campos `videoUrl` e `capaUrl` com as URLs `https://raw.githubusercontent.com/navisantos/mavan-media/main/reels/<pasta>/<arquivo>`, e `status` = `aprovado`.

O vínculo entre vídeo e post é feito **só pelos campos `videoUrl`/`capaUrl` do portal**, nunca pela data ou pelo nome da pasta (a Mariana pode mudar a data de um post).

## Portal de revisão
- Página publicada como artifact (privada; o Ivan convida a Mariana como colaboradora): https://claude.ai/artifact/ELVSd2zJpKaCzFRgARvSkY. O código está em `tools/portal.html`.
- Dados na coleção `posts` do banco do artifact (ferramenta ArtifactData), um documento por post, id = data inicial (`AAAA-MM-DD`). Campos: `date`, `tipo` (B/C), `titulo`, `roteiro` (uma fala por linha, "Mari: ..." / "Cliente: ..."), `legendaIg`, `legendaTt`, `horaIg`, `horaTt`, `status` (rascunho/revisao/aprovado/publicado), `liberado` (boolean), `videoUrl`, `capaUrl`, `notas`, `agendadoEm`, `updatedAt`.
- Ao republicar o portal, manter `capabilities: {db: {}, user: {}}`. Escrever em documentos existentes exige `if_version`.
- Por que não GitHub Pages nem HTML no Drive: o repositório é público (expõe roteiros ainda não publicados), página estática não guarda edições, e Drive não abre HTML como página.

## Publicação (Metricool)
- Marca @mavan.3d no Metricool, fuso America/Sao_Paulo; Instagram + TikTok (conta pessoal).
- Ferramentas: `createScheduledPost` (precisa de URL pública de mídia; Instagram como REEL; marcar conteúdo gerado por IA), `getScheduledPosts`, `updateScheduledPost`, `getBestTimeToPostByNetwork`, análises. Não existe ferramenta para apagar rascunhos. A data não pode estar no passado.
- TikTok em conta pessoal não aceita capa personalizada (só conta Business, que exige CNPJ).
- Horários padrão: Instagram 10h e TikTok 18h, editáveis por post no portal. A curva do Metricool ainda é genérica (conta nova). Os horários vêm sempre do portal; a rotina só informa os melhores horários no relatório.
- Cadência: um vídeo por dia até domingo 15/11/2026, depois a cada dois dias.
- Black Friday: 27/11/2026.

## Rotina diária (tarefa agendada "Rotina diária Mavan 3D")
Roda todo dia às 8h47 (SP): agenda no Metricool os posts liberados que já têm `videoUrl` (sem duplicar), marca `publicado` no portal, confere métricas de 24 h e 72 h (resumo semanal às segundas, comparando B x C), e envia relatório com um bloco de melhores horários. Não produz vídeo e não edita roteiro nem legenda.

Regras de decisão para métricas: abandono alto nos 3 primeiros segundos, trocar gancho e capa; boa retenção com poucos compartilhamentos, CTA mais forte de mandar para um amigo; muitos salvamentos, virar série; muitos comentários "EU", repetir o formato de CTA.

## Código (`tools/`)
- `gen4.py`: motor de personagens e utilidades (Stage com supersampling, `draw_mari`, `draw_cliente`, sincronia labial pelo envelope do áudio, pílulas, logo).
- `gen_bambu_studio.py` e `gen_natal_enfeites.py`: geradores dos vídeos de dica (telas simuladas) e de Natal. `cover_*.py`: capas.
- Dependências: Python 3 com Pillow e numpy, ffmpeg, fonte Poppins instalada em `/usr/share/fonts/truetype/google-fonts/`. O logo está em `tools/assets/logo.jpg`.
- Render: pipe de frames para ffmpeg (libx264, crf 18, preset veryfast), áudio com `atrim/adelay/amix` e `loudnorm` I=-16, AAC 192k.

## Histórico
- 10/11/2026 (C): "5 ajustes do Bambu Studio que o manual não conta". Publicado.
- 11/11/2026 (B): enfeite de Natal com nome da marca e foto da família. Aprovado, agendado pela rotina.
- Calendário completo, roteiros e status: no portal, não aqui (o repositório é público).

## Pendências conhecidas
- Instagram com publicação automática (não rascunho) ainda não foi testado de verdade; o TikTok já foi.
- Vídeo de custo de impressão (12/11): roteiro em revisão; falta decidir se inclui a depreciação da impressora.
- Apagar arquivos de vídeo do repositório público depois de postar é opcional.
