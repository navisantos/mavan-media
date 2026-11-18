# ElevenLabs: referência para os vídeos da Mavan 3D

Resumo em português da documentação oficial, lido em 18/11/2026. **Não é cópia literal.** Para o texto completo e atualizado, abrir as fontes no fim. Leia isto antes de gerar vozes de um vídeo novo (ver "Fluxo de produção", passo 2, no `CLAUDE.md`).

Tudo que está nas seções 1 a 6 vem da documentação. A seção 7 é inferência minha sobre o nosso fluxo e precisa ser testada antes de virar regra.

## 1. Modelos (Text to Speech)

| Modelo | Para que serve | Observações |
|---|---|---|
| **Eleven v4** (`eleven_v4`) | O mais expressivo; é o que usamos | 90+ idiomas, limite de 10.000 caracteres por geração, diálogo com várias vozes, tags de áudio |
| Eleven v4 Turbo | Tempo real (~100 ms) | 90+ idiomas, aceita tags de áudio |
| Eleven v3 (`eleven_v3`) | Entrega dramática | 70+ idiomas, limite de 5.000 caracteres |
| Eleven v3 Conversational | Tempo real (~165 ms) | 70+ idiomas, aceita tags |
| Multilingual v2 | Mais estável em texto longo | 29 idiomas, 10.000 caracteres |
| Flash v2.5 | Mais rápido e barato (~100 ms) | 32 idiomas, 40.000 caracteres, metade do preço por caractere |

As técnicas de prompt do v4 também valem para o v3. Vozes clonadas profissionais (PVC) rendem melhor no v4 do que no v3.

## 2. Tags de áudio (v4 e v3)

- Entram no texto entre colchetes, como `[sarcastic]`, `[explaining]`, `[curious]`, `[whispers]`, `[laughs]`, `[sighs]`. Controlam entrega, efeitos sonoros e sotaque.
- Funcionam melhor quando descrevem claramente a qualidade da voz. Uma tag ambígua pode ser lida como efeito sonoro.
- **A voz importa:** a voz segue a tag com mais fidelidade quando aquele estilo de entrega existe nos dados com que ela foi treinada. Não adianta pedir grito de uma voz calma.
- Emoção pode vir do contexto narrativo ou de tags explícitas. As explícitas são mais previsíveis, mas o modelo pode **falar a tag em voz alta**, então vale ouvir cada take.
- O botão **Enhance** da interface web usa um LLM para sugerir tags sem alterar as palavras. Só existe na interface, não na API.

## 3. Pontuação, pausas e ritmo

- Reticências (`...`) criam pausa. MAIÚSCULAS dão ênfase. A pontuação comum define o ritmo.
- **v4 e v3 não aceitam `<break>` (SSML).** Para pausa, usar tags de áudio, reticências e estrutura do texto. Os modelos antigos aceitam `<break time="x.xs" />` de até 3 s, mas muitos breaks deixam a voz instável.
- Velocidade: parâmetro `speed` de 0.7 a 1.2 (padrão 1.0). Valores extremos pioram a qualidade. O ritmo também depende das amostras de treino da voz.

## 4. Pronúncia e normalização de texto

- **v4:** aceita transcrição fonética **IPA entre barras**, direto no texto. O resultado varia por voz, então testar as palavras importantes.
- Modelos v2: tags de fonema (CMU Arpabet ou IPA), só com `eleven_flash_v2` e só para uma palavra por vez.
- **Alias tags** e **dicionários de pronúncia** (arquivo TXT ou `.PLS`) trocam uma palavra por outra grafia. A busca diferencia maiúsculas de minúsculas e só a primeira regra que casa é aplicada.
- Números, moedas, datas, horas, telefones, URLs, unidades e siglas podem ser lidos errado, principalmente nos modelos pequenos e rápidos. Mitigações: modelo maior, expandir tudo para a forma falada antes de gerar, ou pré-processar o texto com expressões regulares. (É a razão da regra "escrever números e siglas por extenso" do `CLAUDE.md`.)

## 5. Vozes

- Biblioteca com mais de 10.000 vozes da comunidade, clonagem instantânea e profissional, e criação de voz a partir de descrição de texto.
- Diálogo: atribuir uma voz diferente a cada personagem. Existe um endpoint de **Text to Dialogue** além do Text to Speech comum.

## 6. Recursos de geração

- **Efeitos de áudio** (`audio_effects`, nos endpoints Text to Speech e Text to Dialogue, sem custo extra): presets de filtro, distância, ambiente (reverb), ruído de fundo e panorama estéreo. Reverb e panorama geram estéreo, então são recusados em saída PCM/μ-law/A-law mono.
- **Formatos de saída:** MP3 (padrão), PCM, μ-law e A-law (8 kHz), Opus (48 kHz). Qualidades mais altas exigem plano pago.
- **Não determinismo:** a mesma entrada pode gerar áudios diferentes. O parâmetro `seed` melhora a consistência, mas não garante repetição.
- **Texto longo:** dividir em trechos e usar os parâmetros de texto anterior e seguinte (`previous_text` / `next_text`) para manter a prosódia natural entre eles.
- Regenerar o mesmo conteúdo idêntico até 2 vezes é gratuito (segundo a FAQ). Não confiar nisso sem checar; a nossa regra continua sendo **nunca repetir a chamada de geração**.
- Uso comercial exige plano pago.

## 7. Como isso pode melhorar o nosso fluxo (inferência, a testar)

Nada aqui foi testado nos vídeos da Mavan.

1. **Siglas:** hoje escrevemos "pê-éle-á" por extenso. O v4 aceita IPA entre barras, que pode soar mais natural. Testar numa fala curta antes de adotar.
2. **Continuidade entre falas:** geramos 1 take por fala, sem contexto. Se a ferramenta usada expuser `previous_text`/`next_text` (ou o endpoint de diálogo), a conversa entre Mari e cliente pode soar mais fluida. Hoje não sabemos se o conector que usamos expõe esses parâmetros.
3. **Velocidade:** `speed` perto de 1.1 poderia encurtar os vídeos de TikTok que passaram de 60 s, sem cortar texto. Conferir se o conector aceita o parâmetro e se a voz continua natural.
4. **Tags:** manter uma tag por fala, descrevendo a entrega ("[sarcastic]", "[curious]"), e ouvir os takes à procura de tag falada em voz alta.
5. **Efeitos:** um leve ambiente (`audio_effects`) poderia dar mais presença, mas gera estéreo; nosso pipeline hoje converte tudo para mono 44,1 kHz.

## Fontes (documentação oficial)

- Eleven v4, prompting: https://elevenlabs.io/docs/best-practices/prompting/eleven-v4
- Prompting, visão geral: https://elevenlabs.io/docs/best-practices/prompting
- Normalização de texto: https://elevenlabs.io/docs/best-practices/prompting/normalization
- Text to Speech, boas práticas: https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices
- Text to Speech, visão geral: https://elevenlabs.io/docs/overview/capabilities/text-to-speech
