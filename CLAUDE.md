# Mavan 3D: vídeos e publicação (contexto do projeto)

Este arquivo guarda o contexto do projeto para qualquer sessão futura do Claude. Leia antes de produzir ou publicar qualquer coisa.

## Quem e o quê
- Marca: Mavan 3D (@mavan.3d), produtos impressos em 3D. Dono: Ivan (São Paulo). Mariana revisa roteiros e legendas.
- Conteúdo: vídeos verticais 2D animados (1080x1920, 30 fps) para Instagram Reels e TikTok. Personagens: **Mari** (a marca; olhos verdes, sem óculos, avental com coração) e o **cliente** cético (sarcástico).
- Dois públicos: **C** = comunidade 3D (dicas, bastidores) e **B** = cliente final que quer brinde personalizado. **Estratégia desde 14/11/2026:** C vai só no TikTok e B vai só no Instagram (C rendeu bem no TikTok e mal no Instagram; B ao contrário). Dia de postagem tem dois vídeos, um de cada. Mesma duração de antes (~45 s, cerca de 10 falas). Reavaliar cruzar redes com mais dados. Os vídeos B de novembro/dezembro focavam em **Natal** (itens que a pessoa ainda personaliza: nome da marca, foto da família, ano, pintura); desde 23/11 o Ivan quer variar para brindes úteis, nem sempre de Natal (ver regra de 23/11 abaixo).
- Tom: casual, em português do Brasil. O Ivan chama o Claude de "champs"/"capitão".

## Regras de conteúdo
- **Ivan, 23/11/2026 (vídeos B no Instagram):** parar de repetir em todo vídeo o prazo de produção ("cerca de uma semana"); só citar prazo quando o tema do vídeo for o prazo. Parar de usar a etiqueta de presente como exemplo fixo. Preferir **brinde útil**, que a pessoa vai usar, e **não precisa ser de Natal**. Gancho na primeira frase com provocação sobre algo que a pessoa faz (ex.: "Seu cliente joga seu brinde no lixo"), vídeo curto (até ~35 s), um tema só. Os dados de 23/11 mostraram que os Reels com 30% ou menos de abandono nos 3 primeiros segundos foram os que alcançaram mais de mil pessoas.
- **Capa sempre com um pouco do tema do vídeo** (ex.: gorro de Natal na Mari e bolas penduradas). Não reaproveitar capa genérica.
- Roteiro e legendas são da Mariana: o Claude propõe, ela edita no portal. Nunca alterar o texto que ela revisou.
- Só publica o que estiver com a flag **Liberado para publicar** marcada no portal.
- Números e fatos de custo vêm do Ivan (ex.: filamento R$ 100/kg, falha ~20%); energia calculada com 95 W (Bambu Lab A1 do Ivan imprimindo PLA; P1S/X1C seriam 105 W) e tarifa Enel SP com impostos ~R$ 0,98/kWh. Peças de exemplo devem ser rotuladas como ilustrativas.
- Os itens de Natal que a Mavan faz: enfeite com nome da marca + espaço para foto, enfeite com ano gravado, etiqueta de presente que vira enfeite, kit para pintar em casa (o kit inclui tinta). Prazo de produção cerca de 1 semana, inclusive para brindes em quantidade; pedir cedo.

## Fluxo de produção de um vídeo
1. Roteiro aprovado no portal (flag marcada).
2. Vozes na ElevenLabs (modelo `eleven_v4`, tags como `[sarcastic]`, `[explaining]`): voz **Sofia** `n2a9VtkZLl8j1FSXHsL7` para a Mari e **Luciano** `FOhTvAmqIK234DPck9zT` para o cliente. Gera 1 take por fala (cada take custa ~60–140 créditos). Nunca repetir a chamada de geração para "tentar de novo". Escrever números e siglas por extenso na fala ("três D"). **Antes de gerar vozes de um vídeo novo, leia `docs/elevenlabs.md`** (resumo: tags, pronúncia, velocidade, ideias a testar). A página oficial integral em PT-BR está em `docs/elevenlabs-boas-praticas-tts-pt.md`. Para imagem, vídeo generativo e lip sync: `docs/elevenlabs-imagem-video.md` (resumo) e `docs/elevenlabs-imagem-video-pt.md` (íntegro). Vozes (clonagem, Voice Design, **vozes padrão expiram em 31/12/2026**, conferir Sofia e Luciano): `docs/elevenlabs-vozes.md` e `docs/elevenlabs-vozes-pt.md`.
3. Baixar os áudios (o domínio `elevenlabsusercontent.com` precisa estar liberado nas configurações do Claude), converter para WAV mono 44,1 kHz em `tools/aud*/fin/NN.wav`.
4. Copiar `tools/gen_natal_enfeites.py` (modelo mais recente), trocar `LINES`, `TITLES`, as funções de cena e o texto das pílulas finais. `python3 -I gen.py preview` gera um mosaico para conferir; `python3 -I gen.py render` gera o MP4 (~45 s de render).
5. Capa: copiar `tools/cover_natal.py` e adaptar texto, chips e elementos do tema.
6. Colocar a capa no início: `tools/add_cover_frames.sh capa.png video_sem_capa.mp4 video.mp4 [N]` (o TikTok usa o primeiro frame como capa). **Vídeo do TikTok: N=30 (1 s inteiro de capa, áudio atrasado 1 s); Instagram: N=3 (padrão).** Vale para todo vídeo novo; o de 11/11 já foi postado sem isso.
7. Mandar vídeo (já com os 3 frames) e capa para o Ivan aprovar.
8. Aprovado: copiar para `reels/AAAA-MM-DD-slug/video.mp4` e `capa.png`, `git push`, e preencher no portal os campos `videoUrl` e `capaUrl` com as URLs `https://raw.githubusercontent.com/navisantos/mavan-media/main/reels/<pasta>/<arquivo>`, e `status` = `aprovado`.

O vínculo entre vídeo e post é feito **só pelos campos `videoUrl`/`capaUrl` do portal**, nunca pela data ou pelo nome da pasta (a Mariana pode mudar a data de um post).

## Portal de revisão
- Página publicada como artifact (privada; o Ivan convida a Mariana como colaboradora): https://claude.ai/artifact/ELVSd2zJpKaCzFRgARvSkY. O código está em `tools/portal.html`.
- Dados na coleção `posts` do banco do artifact (ferramenta ArtifactData), um documento por post, id = data inicial (`AAAA-MM-DD`). Quando há dois posts na mesma data, o segundo usa id `AAAA-MM-DD-ig` ou `AAAA-MM-DD-tt`; a rotina usa sempre o campo `date`. Campos: `date`, `tipo` (B/C), `redes` (`instagram`, `tiktok` ou `ambas`; ausente = ambas), `titulo`, `roteiro` (uma fala por linha, "Mari: ..." / "Cliente: ..."), `legendaIg`, `legendaTt`, `horaIg`, `horaTt`, `status` (rascunho/revisao/aprovado/publicado), `liberado` (boolean), `videoUrl`, `capaUrl`, `notas`, `agendadoEm`, `updatedAt`.
- Ao republicar o portal, manter `capabilities: {db: {}, user: {}}`. Escrever em documentos existentes exige `if_version`.
- Por que não GitHub Pages nem HTML no Drive: o repositório é público (expõe roteiros ainda não publicados), página estática não guarda edições, e Drive não abre HTML como página.

## Publicação (Metricool)
- Marca @mavan.3d no Metricool, fuso America/Sao_Paulo; Instagram + TikTok (conta pessoal).
- Ferramentas: `createScheduledPost` (precisa de URL pública de mídia; Instagram como REEL; marcar conteúdo gerado por IA), `getScheduledPosts`, `updateScheduledPost`, `getBestTimeToPostByNetwork`, análises. Não existe ferramenta para apagar rascunhos. A data não pode estar no passado.
- TikTok: não ligar a marcação de conteúdo de marca própria (o único vídeo com ela teve 14 views; suspeita, não confirmada). Conta pessoal não aceita capa personalizada (só conta Business, que exige CNPJ).
- Horários padrão: Instagram 10h e TikTok 18h, editáveis por post no portal. A curva do Metricool ainda é genérica (conta nova). Os horários vêm sempre do portal; a rotina só informa os melhores horários no relatório.
- Cadência: postagem diária até domingo 15/11/2026, depois a cada dois dias (17, 19, 21/11...), sempre com um C no TikTok e um B no Instagram.
- Black Friday: 27/11/2026.

## Rotina diária (tarefa agendada "Rotina diária Mavan 3D")
Roda todo dia às 8h47 (SP): agenda no Metricool, só nas redes indicadas em `redes`, os posts liberados que já têm `videoUrl` (sem duplicar), marca `publicado` no portal, confere métricas de 24 h e 72 h (resumo semanal às segundas, comparando B x C), e envia relatório com um bloco de melhores horários. Não produz vídeo e não edita roteiro nem legenda.

Regras de decisão para métricas: abandono alto nos 3 primeiros segundos, trocar gancho e capa; boa retenção com poucos compartilhamentos, CTA mais forte de mandar para um amigo; muitos salvamentos, virar série; muitos comentários "EU", repetir o formato de CTA.

## Código (`tools/`)
- `gen4.py`: motor de personagens e utilidades (Stage com supersampling, `draw_mari`, `draw_cliente`, sincronia labial pelo envelope do áudio, pílulas, logo).
- `gen_bambu_studio.py` e `gen_natal_enfeites.py`: geradores dos vídeos de dica (telas simuladas) e de Natal. `cover_*.py`: capas.
- **Formato novo desde 21/11/2026: vídeo explicativo SEM personagem** (pedido do Ivan: sem esquete, sem Mari/cliente na tela). Só a voz da Sofia narrando (falas continuam com prefixo "Mari:" no portal), cenas desenhadas, **legenda grande queimada no vídeo** (palavra a palavra, ênfase em amarelo) e pílulas finais. Gerador: `tools/gen_explica.py` (`python3 -I gen_explica.py tt|ig preview|render`; para vídeo novo copiar e trocar o dicionário `TT`/`IG`, os áudios em `audNN/fin/NN.wav` e as funções de cena). Capas: `tools/cover_explica.py`. Foto real do kettlebell porta-joias (enviada pelo Ivan): `tools/assets/kettlebell_real.jpg` (usar foto real do produto; desenho de kettlebell só como ilustração, rotulada). Legenda do post (texto da rede) continua escrita no portal (`legendaIg`/`legendaTt`).
- Dependências: Python 3 com Pillow e numpy, ffmpeg, fonte Poppins instalada em `/usr/share/fonts/truetype/google-fonts/`. O logo está em `tools/assets/logo.jpg`.
- Render: pipe de frames para ffmpeg (libx264, crf 18, preset veryfast), áudio com `atrim/adelay/amix` e `loudnorm` I=-16, AAC 192k.

## Histórico
- 10/11/2026 (C): "5 ajustes do Bambu Studio que o manual não conta". Publicado.
- 11/11/2026 (B): enfeite de Natal com nome da marca e foto da família. Publicado pela rotina.
- 12/11/2026 (C): custo de imprimir uma peça (impressora Bambu Lab A1, PLA 95 W). Aprovado, agendado pela rotina.
- 13/11/2026 (B): amigo secreto personalizado (caneca genérica x enfeite com nome ou frase). CTA trocado de "comenta EU" (não funcionou) para "manda para quem tirou você". Postado manualmente no mesmo dia, depois do horário padrão.
- 14/11/2026: estratégia de separar por rede (C no TikTok, B no Instagram). Portal ganhou o campo Redes.
- Calendário completo, roteiros e status: no portal, não aqui (o repositório é público).

- 14/11/2026: C "5 erros da primeira camada" (TikTok, 18h, ~62 s, 1 s de capa) e B "kit para pintar em casa" (Instagram, 10h). Agendados manualmente.

- 15/11/2026: C "sinais de falha" (TikTok) e B "brindes" (Instagram). Publicados.
- 17/11/2026: C "PLA, PETG ou TPU" (TikTok, 20h) e B "etiqueta de presente que vira enfeite" (Instagram, 20h). Publicados. Teste de horário 12h x 18h no TikTok ainda sem dados (as métricas do TikTok de 13 a 15/11 não tinham sincronizado no Metricool).
- 19/11/2026: B "Black Friday: brinde sob medida" (Instagram, 10h, `tools/gen_blackfriday.py`) e C "suporte em árvore" (TikTok, 18h, `tools/gen_suporte.py`). Primeira produção com tags de voz descritivas (`[sarcastic, dry]`, `[explaining, warm, confident]`, `[warm, friendly, upbeat]`) nas falas de gancho e CTA; 22 takes, 1 por fala, ~1.955 créditos. Sofia e Luciano são vozes da Voice Library (não padrão), então não expiram em 31/12. Legendas escritas pelo Claude porque estavam vazias no portal (Mariana pode editar). Agendados pelo Claude a pedido do Ivan, sem passar pela aprovação prévia do vídeo; portal marcado `publicado` para a rotina não duplicar.

- 21/11/2026: primeiros vídeos no formato sem personagem. C "5 problemas de imprimir 3D na praia" (TikTok, 12h, ~74 s, 1 s de capa, `reels/2026-11-21-praia/`) e B "kettlebell porta-joias para treinar nas férias" (Instagram, 10h, ~55 s, `reels/2026-11-21-kettlebell/`). Voz Sofia, 20 takes, ~2.000 créditos. Aguardam aprovação do Ivan e revisão da Mariana. O que Ivan confirmou sobre o kettlebell: cabem aliança e correntinha, abre com rosca, aliança não arranha porque não fica no dedo. Sem promessa de proteção contra roubo. Falta conferir onde fica a rosca (a cena "abre com rosca" é desenho esquemático rotulado como ilustração).

- 23/11/2026: B "brinde que a pessoa usa" (Instagram, 20h, ~34 s, `reels/2026-11-23-brinde/`, `tools/gen_brinde.py`, capa `tools/cover_brinde.py`). Gancho "Seu cliente joga seu brinde no lixo". Fotos e clipe reais enviados pelo Ivan em `tools/assets/brindes/` (ratatouille para chef, pazinha de ração para pet shop, marcador de copo com pet estampado; o clipe de frames `tools/clip23/` não vai para o git). Falta foto de marcador com logo de empresa (no vídeo é só texto). Voz Sofia, 6 takes, ~580 créditos. Legenda escrita pelo Claude. Aprovado pelo Ivan e agendado.

- 23/11/2026: C "custo real com falha de 20%" (TikTok, agendado 20h porque a aprovação veio depois das 18h, ~48 s, 1 s de capa, `reels/2026-11-23-falha/`, `tools/gen_falha.py`, capa `tools/cover_falha.py`). Gancho "Filamento a cem reais o quilo parece barato. Até uma em cada cinco peças falhar." Números do Ivan (R$ 100/kg, falha ~20%); R$ 125 por kg de peça boa é cálculo do Claude (100 / 0,8, só filamento). Cenas todas ilustrativas. Voz Sofia, 7 takes, ~790 créditos. Legenda escrita pelo Claude.

## Pendências conhecidas
- Depreciação da impressora não entrou no vídeo de custo; se entrar numa próxima versão, falta o preço da A1.
- Apagar arquivos de vídeo do repositório público depois de postar é opcional.

- 25/11/2026: B "plaquinha com o nome do pet: a Mila na praia" (Instagram, agendado 12h, ~24 s, 3 frames de capa, `reels/2026-11-25-mila/`, `tools/gen_mila.py`, capa `tools/cover_mila.py`). Vídeo-base criado pelo Ivan no ElevenLabs (Mila, shiba, imagens geradas por IA); o Claude só editou: áudio original removido, voz Sofia (5 takes, ~405 créditos), legenda queimada, logo, rótulo "ilustração gerada por IA" queimado, CTA "PET". Post marcado como conteúdo de IA. Sem prazo, preço nem cor (não confirmados). Pendência: Ivan confirmar se a plaquinha vem em outras cores/formatos. Substituiu o rascunho "ano gravado".

- 26/11/2026: C "como secar filamento sem estufa" (TikTok, agendado 18h, ~55 s, 1 s de capa, `reels/2026-11-26-seca/`, `tools/gen_seca.py`, capa `tools/cover_seca.py`). Roteiro reescrito 3 vezes a pedido do Ivan (a estufa saiu: ninguém tem; micro-ondas entrou só como "nem tenta", porque os guias desaconselham). Conteúdo de conhecimento geral e pesquisa web (All3DP, eufymake), sem números nem temperaturas; a fala da cama aquecida com caixa não foi testada pelo Ivan. Cenas todas ilustrativas. Voz Sofia, 6 takes, ~860 créditos. Agendado com a aprovação do Ivan, sem a flag da Mariana. Legenda escrita pelo Claude.
