# ElevenLabs: imagem e vídeo (resumo para os vídeos da Mavan 3D)

Resumo do catálogo "Imagem e Vídeo" da ElevenLabs, enviado pelo Ivan em 18/11/2026. **Texto integral (PT-BR): `docs/elevenlabs-imagem-video-pt.md`.** Em caso de dúvida vale o texto integral. O catálogo muda com frequência; conferir os modelos disponíveis na ferramenta antes de planejar.

Hoje os vídeos da Mavan são **animação 2D feita em código** (Python/Pillow/ffmpeg, personagens Mari e cliente, boca sincronizada pelo envelope do áudio). Nada abaixo foi testado nos nossos vídeos. As ideias na seção 6 são inferência minha.

## 1. Planos, limites e custo
- Plano gratuito: só imagens, no máximo 3 por dia. **Vídeo exige plano pago.** Uso pela API exige plano Pro ou superior.
- Modelos da ByteDance (Seedance, Seedream) ficam desativados por padrão na API e precisam de aprovação.
- Vários modelos não estão disponíveis nos Estados Unidos (a página marca cada um).
- **Custo de todos os modelos "varia conforme as configurações e a duração".** A página não dá preço. Antes de gerar em lote, estimar o custo (a ferramenta de fala tem `estimate_only`; conferir se a de vídeo também tem) e combinar com o Ivan.
- Gerações em lote: até 4 por vez na maioria dos modelos. Nossa regra de nunca repetir a chamada vale também aqui.

## 2. Vídeo generativo com 9:16 (formato Reels/TikTok)
| Modelo | Duração | Resolução | Observações |
|---|---|---|---|
| Google Veo 3.1 (e Fast, Lite) | 4, 6 ou 8 s fixos | 720p/1080p (Lite: só 720p) | 16:9 e 9:16. Áudio integrado, diálogo, sincronização labial e efeitos. Ligar ou desligar o som muda o custo |
| Seedance 2.0 (Fast, Mini) | 4 a 15 s | até 1080p (Fast/Mini: 720p) | Várias proporções, inclusive 9:16. Referências de imagem, vídeo e áudio. Áudio e vídeo gerados juntos |
| **Seedance 2.5** | 4 a 30 s | 480p/720p | Até 30 referências de imagem, 10 de vídeo, 10 de áudio. Aceita só áudio de referência. **Sem controle de seed** |
| Kling 3.0 | 3 a 15 s | só 1080p | 16:9, 1:1, 9:16. Boa consistência de personagem. Sincronização labial multilíngue |
| Gemini Omni Flash 1.1 | 3 a 10 s | até 4K | 16:9 e 9:16 |
| Wan 2.5 / 2.6 / 3.0, Runway Gen-4.5, LTX, FLUX 3, MiniMax H3 | variam | variam | Ver arquivo integral |

Edição e extensão de vídeo existente: Seedance 2.5 Video Edit e Video Extend (até 30 s de entrada), Kling O3 Edit, Runway Aleph.

## 3. Imagem generativa
- **Nano Banana 2 / 2.1 / Pro:** aderência forte ao prompt, **texto legível em vários idiomas**, identidade consistente entre personagens e objetos, várias imagens de referência (2.1: até 14), 9:16 e até 4K. O Pro mantém a semelhança de até 5 pessoas.
- **GPT Image 2.5 (Sunburst, Flare):** até 10 referências, até 4K, 9:16, cinco níveis de qualidade, bom para edição precisa.
- Também: Krea 2, Recraft V4/V4.1, Seedream, FLUX, Runway Gen-4 Image. Detalhes no arquivo integral.
- Ampliação com Topaz (1.25x a 4x). Remoção de fundo gera PNG com transparência.

## 4. Sincronização labial (lip sync)
- **Imagem + áudio → personagem falando:** Creatify Aurora (480p/720p, piscadas, respiração e gestos a partir do tom da voz), Veed Fabric, HeyGen Avatar 4, OmniHuman 1.5, MiniMax H3 Max Lip Sync (áudio de 5 a 14,8 s).
- **Vídeo + áudio → boca refeita:** Sync 3, Sync Lipsync 2 Pro (saída até 4K, "otimizado para live-action, animação 3D e vídeos gerados por IA"), Veed Lipsync e Lipsync 2.0.
- Todos dizem que a imagem ou vídeo precisa ter **uma figura detectável / rosto claramente visível**. **A documentação não fala de desenho 2D estilo cartum**; só testando para saber se a Mari e o cliente funcionam.

## 5. Utilitários
Topaz Image/Video Upscale (até 4x, com conversão de taxa de quadros até 60 fps), remoção de fundo de imagem e de vídeo (fundo transparente, preto ou verde), Runway Ruby (SDR para HDR).

## 6. Ideias para evoluir os vídeos (inferência, a testar)
1. **Cenas de produto reais ou fotográficas.** Nano Banana ou GPT Image poderiam gerar cenários (árvore, mesa de Natal) ou fotos de ambiente. **Cuidado:** imagem de IA de um produto que a Mavan faz pode enganar o cliente sobre o resultado final. Para produto, preferir foto real do Ivan; imagem gerada só como cenário, e sempre rotulada como ilustrativa (já marcamos "conteúdo gerado por IA" no Instagram e no TikTok).
2. **Personagens consistentes em imagem.** Gerar a Mari em poses e cenários novos com a arte atual como referência, mantendo olhos verdes, sem óculos e avental com coração (regras do `CLAUDE.md`).
3. **Fala animada pelo áudio da ElevenLabs.** Se um modelo de imagem + áudio funcionar com a Mari, o áudio atual (Sofia/Luciano) alimentaria a boca. Hoje a sincronização é calculada em código, e é boa o bastante, então só vale se o ganho de naturalidade compensar o custo.
4. **Clipes curtos de Veo ou Seedance** (4 a 8 s) como cena de ilustração entre falas, no lugar de algumas cenas de janela. 9:16 é suportado. Como o áudio é gerado junto, desligar o som (custa menos) e manter nossa trilha.
5. **Resolução e fps:** nosso render é 1080x1920 a 30 fps. Upscale não é necessário.
6. **Marca e fidelidade:** a Mari é a marca. Qualquer arte nova precisa passar pelo Ivan antes de entrar em vídeo, como as capas.

## Fonte
Catálogo "Imagem e Vídeo" (ElevenLabs), conforme colado pelo Ivan: `docs/elevenlabs-imagem-video-pt.md`. Documentação oficial: https://elevenlabs.io/docs
