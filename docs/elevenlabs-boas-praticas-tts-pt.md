---

title: Práticas recomendadas
subtitle: >-
Saiba como controlar a entonação, a pronúncia e a emoção, além de otimizar
texto para fala.
----------------

Este guia apresenta técnicas para aprimorar os resultados de conversão de texto em fala usando os modelos da ElevenLabs. Experimente esses métodos para descobrir o que funciona melhor para suas necessidades.

## Controles

<Info>
  Estamos trabalhando ativamente no *Modo Diretor* para dar a você ainda mais controle sobre os resultados.
</Info>

Essas técnicas oferecem uma maneira prática de alcançar resultados mais sutis até que recursos avançados, como o *Modo Diretor*, sejam lançados.

### Pausas

<Info>
  Eleven v4 e Eleven v3 não oferecem suporte a tags de pausa do SSML. Use as técnicas descritas na seção
  [Como criar prompts para o Eleven v4](#prompting-eleven-v4) para controlar as pausas.
</Info>

Use `<break time="x.xs" />` para pausas naturais de até 3 segundos.

<Note>
  Usar muitas tags de pausa em uma única geração pode causar instabilidade. A IA pode acelerar ou
  introduzir ruídos adicionais ou artefatos de áudio. Estamos trabalhando para resolver isso.
</Note>

```text Exemplo
"Hold on, let me think." <break time="1.5s" /> "Alright, I've got it."
```

* **Consistência:** use tags `<break>` de forma consistente para manter um fluxo de fala natural. O uso excessivo pode causar instabilidade.
* **Comportamento específico da voz:** vozes diferentes podem lidar com pausas de maneiras diferentes, especialmente as treinadas com sons de preenchimento, como "uh" ou "ah".

Alternativas a `<break>` incluem travessões (- ou --) para pausas curtas ou reticências (...) para tons hesitantes. No entanto, elas são menos consistentes.

```text Exemplo

"It… well, it might work." "Wait — what's that noise?"

```

### Pronúncia

#### IPA com o Eleven v4

O [Eleven v4](/docs/pt/overview/capabilities/text-to-speech/eleven-v4) (`eleven_v4`) inclui suporte nativo aprimorado ao Alfabeto Fonético Internacional, ou IPA, dando a você um controle mais preciso sobre a pronúncia de nomes, termos técnicos e outras palavras que exigem tratamento especial. A pronúncia com IPA é mais consistente do que em modelos anteriores, mas os resultados ainda podem variar conforme a voz e a frase. Recomendamos testar pronúncias importantes com a voz escolhida antes de usá-las em produção.

Ao contrário de modelos mais antigos que exigem tags de fonemas no estilo XML, o Eleven v4 entende símbolos IPA quando eles são colocados entre barras no texto:

```text Sintaxe
"/IPA_transcription/"
```

A transcrição IPA deve:

* Estar entre barras (`/`) no início e no fim
* Ser escrita usando símbolos IPA padrão
* Estar entre aspas duplas quando for passada como parâmetro de string

**Exemplos de código**

<CodeBlocks>
  ```python title="Python"
  from elevenlabs import ElevenLabs

  client = ElevenLabs()
  audio = client.text_to_speech.convert(
      voice_id="21m00Tcm4TlvDq8ikWAM",
      text='The term "/ˌbaɪoʊˈkemɪstri/" refers to the study of chemical processes.',
      model_id="eleven_v4",
  )
  ```

  ```typescript title="TypeScript"
  import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

  const client = new ElevenLabsClient();

  const audio = await client.textToSpeech.convert("21m00Tcm4TlvDq8ikWAM", {
    text: 'The city of "/ˌsænfrənˈsɪskoʊ/" is located in California.',
    modelId: "eleven_v4",
  });
  ```

  ```bash title="cURL"
  curl -X POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id} \
    -H "xi-api-key: YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "text": "The concept of \"/fəˈnɛtɪks/\" is central to linguistics.",
      "model_id": "eleven_v4"
    }'
  ```
</CodeBlocks>

Você pode incluir várias transcrições IPA em uma única string de texto:

<CodeBlocks>
  ```python title="Python"
  from elevenlabs import ElevenLabs

  client = ElevenLabs()
  text = 'The medication "/ɡluːˈkoʊs/" and "/ˌɪnsjəˈlɪn/" are commonly used to manage conditions like "/ˌdaɪəˈbiːtiːz/".'
  audio = client.text_to_speech.convert(
      voice_id="21m00Tcm4TlvDq8ikWAM",
      text=text,
      model_id="eleven_v4",
  )
  ```

  ```typescript title="TypeScript"
  import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

  const client = new ElevenLabsClient();
  const text =
    'The medication "/ɡluːˈkoʊs/" and "/ˌɪnsjəˈlɪn/" are commonly used to manage conditions like "/ˌdaɪəˈbiːtiːz/".';
  const audio = await client.textToSpeech.convert("21m00Tcm4TlvDq8ikWAM", {
    text,
    modelId: "eleven_v4",
  });
  ```
</CodeBlocks>

**Boas práticas**

* Use símbolos IPA padrão da [tabela do Alfabeto Fonético Internacional](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet)
* Inclua marcadores de tonicidade: acento primário (ˈ) e secundário (ˌ) para palavras com várias sílabas
* Aplique de forma seletiva: envolva apenas palavras ou frases específicas que precisem de controle de pronúncia
* Teste com sua voz: vozes diferentes podem interpretar o IPA de maneiras ligeiramente distintas

**Solução de problemas**

<AccordionGroup>
  <Accordion title="A pronúncia ainda está incorreta">
    Verifique se sua transcrição IPA está correta usando um dicionário de IPA. Inclua marcadores de tonicidade (ˈ para
    acento primário e ˌ para acento secundário) em palavras com várias sílabas. Teste com vozes diferentes, pois
    algumas podem interpretar o IPA com mais precisão do que outras.
  </Accordion>

  <Accordion title="Resultados inconsistentes com o mesmo IPA">
    A pronúncia IPA é mais consistente do que em modelos anteriores, mas os resultados ainda podem variar conforme a
    voz e a frase. Recomendamos testar pronúncias importantes com a voz escolhida antes de usá-las em produção.
    Se precisar de um resultado consistente, gere mais de uma vez e selecione o melhor resultado.
  </Accordion>
</AccordionGroup>

#### Tags de fonemas para modelos v2

Especifique a pronúncia usando [tags de fonemas SSML](https://en.wikipedia.org/wiki/Speech_Synthesis_Markup_Language) com modelos v2. Os alfabetos compatíveis incluem o Arpabet [CMU](https://en.wikipedia.org/wiki/CMU_Pronouncing_Dictionary) e o [Alfabeto Fonético Internacional (IPA)](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet).

<Note>
  As tags de fonemas são compatíveis apenas com o [modelo](/docs/pt/overview/models) `eleven_flash_v2`.
</Note>

<CodeBlocks>
  ```xml Exemplo de CMU Arpabet
  <phoneme alphabet="cmu-arpabet" ph="M AE1 D IH0 S AH0 N">
    Madison
  </phoneme>
  ```

  ```xml Exemplo de IPA
  <phoneme alphabet="ipa" ph="ˈæktʃuəli">
    actually
  </phoneme>
  ```
</CodeBlocks>

Recomendamos usar CMU Arpabet para obter resultados consistentes e previsíveis com modelos v2. Embora o IPA possa ser eficaz, o CMU Arpabet geralmente oferece um desempenho mais confiável.

As tags de fonemas funcionam apenas para palavras individuais. Se você tiver um nome com nome e sobrenome cuja pronúncia queira definir de uma determinada maneira, será necessário criar uma tag de fonema para cada palavra.

Garanta a marcação de tonicidade correta para palavras com várias sílabas e mantenha uma pronúncia precisa:

<CodeBlocks>
  ```xml Uso correto
  <phoneme alphabet="cmu-arpabet" ph="P R AH0 N AH0 N S IY EY1 SH AH0 N">
    pronunciation
  </phoneme>
  ```

  ```xml Uso incorreto
  <phoneme alphabet="cmu-arpabet" ph="P R AH N AH N S IY EY SH AH N">
    pronunciation
  </phoneme>
  ```
</CodeBlocks>

#### Tags de alias

Para modelos que não oferecem suporte a tags de fonemas, você pode tentar escrever as palavras de forma mais fonética. Também é possível usar vários recursos, como letras maiúsculas, hífens, apóstrofos ou até aspas simples em torno de uma ou mais letras.

Por exemplo, uma palavra como "trapezii" poderia ser escrita como "trapezIi" para dar mais ênfase ao "ii" da palavra.

Você pode substituir a palavra diretamente no texto ou, se quiser especificar a pronúncia usando outras palavras ou frases ao usar um dicionário de pronúncia, pode usar tags de alias. Isso pode ser útil se você estiver gerando conteúdo com o Multilingual v2, que não oferece suporte a tags de fonemas. Você pode usar dicionários de pronúncia com o ElevenCreative Studio, o Dubbing Studio e a Síntese de fala pela API.

Por exemplo, se o texto incluir um nome com uma pronúncia incomum que a IA possa ter dificuldade em interpretar, use uma tag de alias para especificar como ele deve ser pronunciado:

```
  <lexeme>
    <grapheme>Claughton</grapheme>
    <alias>Cloffton</alias>
  </lexeme>
```

Se quiser garantir que uma sigla seja sempre pronunciada de determinada forma quando aparecer no texto, use uma tag de alias para especificar isso:

```
  <lexeme>
    <grapheme>UN</grapheme>
    <alias>United Nations</alias>
  </lexeme>
```

#### Dicionários de pronúncia

Algumas de nossas ferramentas, como o ElevenCreative Studio e o Dubbing Studio, permitem criar e enviar um dicionário de pronúncia. Com eles, você pode especificar a pronúncia de determinadas palavras, como nomes de personagens ou marcas, ou definir como siglas devem ser lidas.

Os dicionários de pronúncia oferecem essa funcionalidade permitindo o envio de um arquivo de léxico ou dicionário que especifica pares de palavras e como elas devem ser pronunciadas, usando um alfabeto fonético ou substituições de palavras.

Sempre que uma dessas palavras for encontrada em um projeto, o modelo de IA pronunciará a palavra usando a substituição especificada.

Para fornecer um arquivo de dicionário de pronúncia, abra as configurações de um projeto e envie um arquivo em formato TXT ou [.PLS](https://www.w3.org/TR/pronunciation-lexicon/). Quando um dicionário é adicionado a um projeto, ele recalcula automaticamente quais partes do projeto precisarão ser reconvertidas usando o novo arquivo de dicionário e as marca como não convertidas.

No momento, oferecemos suporte apenas a dicionários de pronúncia que especificam substituições usando tags de fonemas ou alias.

Tanto fonemas quanto aliases são conjuntos de regras que especificam uma palavra ou frase que procuram, chamada de grafema, e pelo que ela será substituída. Observe que as buscas diferenciam maiúsculas de minúsculas. Ao verificar uma palavra de substituição em um dicionário de pronúncia, o dicionário é verificado do início ao fim, e apenas a primeira substituição é usada.

#### Exemplos de dicionários de pronúncia

Veja exemplos de dicionários de pronúncia em CMU Arpabet e IPA, incluindo um fonema para especificar a pronúncia de "Apple" e um alias para substituir "UN" por "United Nations":

<CodeBlocks>
  ```xml Exemplo de CMU Arpabet
  <?xml version="1.0" encoding="UTF-8"?>
  <lexicon version="1.0"
        xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
          http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
        alphabet="cmu-arpabet" xml:lang="en-GB">
    <lexeme>
      <grapheme>apple</grapheme>
      <phoneme>AE P AH L</phoneme>
    </lexeme>
    <lexeme>
      <grapheme>UN</grapheme>
      <alias>United Nations</alias>
    </lexeme>
  </lexicon>
  ```

  ```xml Exemplo de IPA
  <?xml version="1.0" encoding="UTF-8"?>
  <lexicon version="1.0"
        xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
          http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
        alphabet="ipa" xml:lang="en-GB">
    <lexeme>
      <grapheme>Apple</grapheme>
      <phoneme>ˈæpl̩</phoneme>
    </lexeme>
    <lexeme>
      <grapheme>UN</grapheme>
      <alias>United Nations</alias>
    </lexeme>
  </lexicon>
  ```
</CodeBlocks>

Para gerar um arquivo de dicionário de pronúncia `.pls`, há algumas ferramentas de código aberto disponíveis:

* [Sequitur G2P](https://github.com/sequitur-g2p/sequitur-g2p) - Ferramenta de código aberto que aprende regras de pronúncia a partir de dados e pode gerar transcrições fonéticas.
* [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus) - Sistema G2P de código aberto treinado com dicionários existentes, como o CMUdict.
* [eSpeak](https://github.com/espeak-ng/espeak-ng) - Sintetizador de fala que pode gerar transcrições de fonemas a partir de texto.
* [CMU Pronouncing Dictionary](https://github.com/cmusphinx/cmudict) - Dicionário de inglês pronto com transcrições fonéticas.

### Emoção

Transmita emoções por meio do contexto narrativo ou de tags explícitas de diálogo. Essa abordagem ajuda a IA a entender o tom e a emoção que deve reproduzir.

```text Exemplo
You're leaving?" she asked, her voice trembling with sadness. "That's it!" he exclaimed triumphantly.
```

Tags explícitas de diálogo geram resultados mais previsíveis do que depender apenas do contexto, mas o modelo ainda falará as orientações de entrega emocional. Elas podem ser removidas na pós-produção usando um editor de áudio, se não forem desejadas.

### Ritmo

O ritmo do áudio é altamente influenciado pelo áudio usado para criar a voz. Ao criar sua voz, recomendamos usar amostras mais longas e contínuas para evitar problemas de ritmo, como uma fala artificialmente rápida.

Para controlar a velocidade do áudio gerado, você pode usar a configuração de velocidade. Ela permite acelerar ou desacelerar a fala gerada. A configuração de velocidade está disponível no Text to Speech pelo site e pela API, bem como no ElevenCreative Studio e na Plataforma de Agentes. Ela pode ser encontrada nas configurações de voz.

O valor padrão é 1.0, o que significa que a velocidade não é ajustada. Valores abaixo de 1.0 desaceleram a voz, até o mínimo de 0.7. Valores acima de 1.0 aceleram a voz, até o máximo de 1.2. Valores extremos podem afetar a qualidade da fala gerada.

O ritmo também pode ser controlado escrevendo em um estilo natural e narrativo.

```text Exemplo
"I… I thought you'd understand," he said, his voice slowing with disappointment.
```

### Dicas

<AccordionGroup>
  <Accordion title="Problemas comuns">
    <ul>
      <li>
        Pausas inconsistentes: certifique-se de que a sintaxe <code>\<break time="x.xs" /></code> seja usada para
        pausas.
      </li>

      <li>
        Erros de pronúncia: use tags de fonemas CMU Arpabet ou IPA para uma pronúncia precisa.
      </li>

      <li>
        Emoção inadequada: adicione contexto narrativo ou tags explícitas para orientar a emoção.{" "}
        <strong>Lembre-se de remover qualquer texto de orientação emocional na pós-produção.</strong>
      </li>
    </ul>
  </Accordion>

  <Accordion title="Dicas para melhorar o resultado">
    Experimente formas alternativas de escrever para alcançar o ritmo ou a emoção desejados. Para efeitos sonoros
    complexos, divida os prompts em elementos menores e sequenciais e combine os resultados manualmente.
  </Accordion>
</AccordionGroup>

### Controle criativo

Embora estejamos desenvolvendo ativamente um "Modo Diretor" para dar aos usuários ainda mais controle sobre os resultados, estas são algumas técnicas provisórias para maximizar a criatividade e a precisão:

<Steps>
  ### Estilo narrativo

  Escreva prompts em estilo narrativo, semelhante à escrita de roteiros, para orientar o tom e o ritmo com eficiência.

  ### Resultados em camadas

  Gere efeitos sonoros ou fala em segmentos e sobreponha-os usando um software de edição de áudio para criar composições mais complexas.

  ### Experimentação fonética

  Se a pronúncia não estiver perfeita, experimente grafias alternativas ou aproximações fonéticas para alcançar os resultados desejados.

  ### Ajustes manuais

  Combine efeitos sonoros individuais manualmente na pós-produção para sequências que exigem uma sincronização precisa.

  ### Iteração com feedback

  Melhore os resultados ajustando descrições, tags ou indicações emocionais.
</Steps>

## Normalização de texto

Ao usar Text to Speech com itens complexos, como números de telefone, CEPs e e-mails, eles podem ser pronunciados incorretamente. Isso costuma acontecer porque esses itens específicos não estão no conjunto de treinamento e modelos menores não conseguem generalizar como devem ser pronunciados. Este guia esclarece quando essas diferenças ocorrem e como fazer com que sejam pronunciados corretamente.

<Tip>
  A normalização é ativada por padrão em todos os modelos de TTS para ajudar a melhorar a pronúncia de números,
  datas e outros elementos de texto complexos.
</Tip>

### Por que os modelos leem as entradas de formas diferentes?

Alguns modelos são treinados para ler números e frases de uma maneira mais humana. Por exemplo, a expressão "\$1,000,000" é lida corretamente como "um milhão de dólares" pelo modelo Eleven Multilingual v2. No entanto, a mesma expressão é lida como "mil mil dólares" pelo modelo Eleven Flash v2.5.

Isso acontece porque o modelo Multilingual v2 é maior e consegue generalizar melhor a leitura de números de uma forma mais natural para ouvintes humanos, enquanto o modelo Flash v2.5 é muito menor e, por isso, não consegue.

#### Exemplos comuns

Os modelos de Text to Speech podem ter dificuldade com os seguintes itens:

* Números de telefone ("123-456-7890")
* Moedas ("\$47,345.67")
* Eventos de calendário ("2024-01-01")
* Horários ("9:23 AM")
* Endereços ("123 Main St, Anytown, USA")
* URLs ("example.com/link/to/resource")
* Abreviações de unidades ("TB" em vez de "Terabyte")
* Atalhos ("Ctrl + Z")

### Como mitigar

#### Use modelos treinados

A maneira mais simples de mitigar isso é usar um modelo de TTS treinado para ler números e frases de uma forma mais humana, como o modelo Eleven Multilingual v2. No entanto, isso nem sempre é possível, por exemplo, se você tiver um caso de uso em que a baixa latência seja essencial (como agentes conversacionais).

#### Aplique normalização em prompts de LLM

Ao usar um LLM para gerar o texto para TTS, você pode adicionar instruções de normalização ao prompt.

<Steps>
  <Step title="Use prompts claros e explícitos">
    LLMs respondem melhor a instruções estruturadas e explícitas. Seu prompt deve especificar claramente que você quer que o texto seja convertido em um formato legível para fala.
  </Step>

  <Step title="Lide com diferentes formatos de números">
    Nem todos os números são lidos da mesma forma. Considere como diferentes tipos de números devem ser falados:

    * Números cardinais: 123 → "cento e vinte e três"
    * Números ordinais: 2nd → "segundo"
    * Valores monetários: \$45.67 → "quarenta e cinco dólares e sessenta e sete centavos"
    * Números de telefone: "123-456-7890" → "um dois três, quatro cinco seis, sete oito nove zero"
    * Decimais e frações: "3.5" → "três vírgula cinco", "⅔" → "dois terços"
    * Algarismos romanos: "XIV" → "quatorze" (ou "o décimo quarto" se for um título)
  </Step>

  <Step title="Remova ou expanda abreviações">
    Abreviações comuns devem ser expandidas para maior clareza:

    * "Dr." → "Doutor"
    * "Ave." → "Avenida"
    * "St." → "Rua" (mas "St. Patrick" deve permanecer)

    Você pode solicitar uma expansão explícita no seu prompt:

    > Expanda todas as abreviações para suas formas completas faladas.
  </Step>

  <Step title="Normalização alfanumérica">
    Nem toda normalização envolve números; algumas expressões alfanuméricas também devem ser normalizadas para maior clareza:

    * Atalhos: "Ctrl + Z" → "control z"
    * Abreviações de unidades: "100km" → "cem quilômetros"
    * Símbolos: "100%" → "cem por cento"
    * URLs: "elevenlabs.io/docs" → "eleven labs ponto io barra docs"
    * Eventos de calendário: "2024-01-01" → "primeiro de janeiro de dois mil e vinte e quatro"
  </Step>

  <Step title="Considere casos extremos">
    Contextos diferentes podem exigir conversões diferentes:

    * Datas: "01/02/2023" → "dois de janeiro de dois mil e vinte e três" ou "primeiro de fevereiro de dois mil e vinte e três" (dependendo da localidade)
    * Horário: "14:30" → "duas e trinta da tarde"

    Se precisar de um formato específico, informe-o explicitamente no prompt.
  </Step>
</Steps>

##### Juntando tudo

Este prompt é um bom ponto de partida para a maioria dos casos de uso:

```text maxLines=0
Convert the output text into a format suitable for text-to-speech. Ensure that numbers, symbols, and abbreviations are expanded for clarity when read aloud. Expand all abbreviations to their full spoken forms.

Example input and output:

"$42.50" → "forty-two dollars and fifty cents"
"£1,001.32" → "one thousand and one pounds and thirty-two pence"
"1234" → "one thousand two hundred thirty-four"
"3.14" → "three point one four"
"555-555-5555" → "five five five, five five five, five five five five"
"2nd" → "second"
"XIV" → "fourteen" - unless it's a title, then it's "the fourteenth"
"3.5" → "three point five"
"⅔" → "two-thirds"
"Dr." → "Doctor"
"Ave." → "Avenue"
"St." → "Street" (but saints like "St. Patrick" should remain)
"Ctrl + Z" → "control z"
"100km" → "one hundred kilometers"
"100%" → "one hundred percent"
"elevenlabs.io/docs" → "eleven labs dot io slash docs"
"2024-01-01" → "January first, two-thousand twenty-four"
"123 Main St, Anytown, USA" → "one two three Main Street, Anytown, United States of America"
"14:30" → "two thirty PM"
"01/02/2023" → "January second, two-thousand twenty-three" or "the first of February, two-thousand twenty-three", depending on locale of the user
```

#### Use expressões regulares para pré-processamento

Se você usa código para criar um prompt para um LLM, pode usar expressões regulares para normalizar o texto antes de fornecê-lo ao modelo. Essa é uma técnica mais avançada e exige algum conhecimento de expressões regulares. Veja alguns exemplos simples:

<CodeBlocks>
  ```python title="normalize_text.py" maxLines=0
  # Be sure to install the inflect library before running this code
  import inflect
  import re

  # Initialize inflect engine for number-to-word conversion
  p = inflect.engine()

  def normalize_text(text: str) -> str:
      # Convert monetary values
      def money_replacer(match):
          currency_map = {"$": "dollars", "£": "pounds", "€": "euros", "¥": "yen"}
          currency_symbol, num = match.groups()

          # Remove commas before parsing
          num_without_commas = num.replace(',', '')

          # Check for decimal points to handle cents
          if '.' in num_without_commas:
              dollars, cents = num_without_commas.split('.')
              dollars_in_words = p.number_to_words(int(dollars))
              cents_in_words = p.number_to_words(int(cents))
              return f"{dollars_in_words} {currency_map.get(currency_symbol, 'currency')} and {cents_in_words} cents"
          else:
              # Handle whole numbers
              num_in_words = p.number_to_words(int(num_without_commas))
              return f"{num_in_words} {currency_map.get(currency_symbol, 'currency')}"

      # Regex to handle commas and decimals
      text = re.sub(r"([$£€¥])(\d+(?:,\d{3})*(?:\.\d{2})?)", money_replacer, text)

      # Convert phone numbers
      def phone_replacer(match):
          return ", ".join(" ".join(p.number_to_words(int(digit)) for digit in group) for group in match.groups())

      text = re.sub(r"(\d{3})-(\d{3})-(\d{4})", phone_replacer, text)

      return text

  # Example usage
  print(normalize_text("$1,000"))   # "one thousand dollars"
  print(normalize_text("£1000"))   # "one thousand pounds"
  print(normalize_text("€1000"))   # "one thousand euros"
  print(normalize_text("¥1000"))   # "one thousand yen"
  print(normalize_text("$1,234.56"))   # "one thousand two hundred thirty-four dollars and fifty-six cents"
  print(normalize_text("555-555-5555"))  # "five five five, five five five, five five five five"

  ```

  ```typescript title="normalizeText.ts" maxLines=0
  // Be sure to install the number-to-words library before running this code
  import { toWords } from "number-to-words";

  function normalizeText(text: string): string {
    return (
      text
        // Convert monetary values (e.g., "$1000" → "one thousand dollars", "£1000" → "one thousand pounds")
        .replace(/([$£€¥])(\d+(?:,\d{3})*(?:\.\d{2})?)/g, (_, currency, num) => {
          // Remove commas before parsing
          const numWithoutCommas = num.replace(/,/g, "");

          const currencyMap: { [key: string]: string } = {
            $: "dollars",
            "£": "pounds",
            "€": "euros",
            "¥": "yen",
          };

          // Check for decimal points to handle cents
          if (numWithoutCommas.includes(".")) {
            const [dollars, cents] = numWithoutCommas.split(".");
            return `${toWords(Number.parseInt(dollars))} ${currencyMap[currency] || "currency"}${cents ? ` and ${toWords(Number.parseInt(cents))} cents` : ""}`;
          }

          // Handle whole numbers
          return `${toWords(Number.parseInt(numWithoutCommas))} ${currencyMap[currency] || "currency"}`;
        })

        // Convert phone numbers (e.g., "555-555-5555" → "five five five, five five five, five five five five")
        .replace(/(\d{3})-(\d{3})-(\d{4})/g, (_, p1, p2, p3) => {
          return `${spellOutDigits(p1)}, ${spellOutDigits(p2)}, ${spellOutDigits(p3)}`;
        })
    );
  }

  // Helper function to spell out individual digits as words (for phone numbers)
  function spellOutDigits(num: string): string {
    return num
      .split("")
      .map((digit) => toWords(Number.parseInt(digit)))
      .join(" ");
  }

  // Example usage
  console.log(normalizeText("$1,000")); // "one thousand dollars"
  console.log(normalizeText("£1000")); // "one thousand pounds"
  console.log(normalizeText("€1000")); // "one thousand euros"
  console.log(normalizeText("¥1000")); // "one thousand yen"
  console.log(normalizeText("$1,234.56")); // "one thousand two hundred thirty-four dollars and fifty-six cents"
  console.log(normalizeText("555-555-5555")); // "five five five, five five five, five five five five"
  ```
</CodeBlocks>

## Como criar prompts no Eleven v4

Esta seção foi escrita para o Eleven v4. Muitas das técnicas abaixo também se aplicam ao [Eleven v3](#prompting-eleven-v3). Em geral, o Eleven v4 representa uma evolução em relação ao Eleven v3, oferecendo resultados melhores em quase todos os casos. Recomendamos fortemente migrar para o v4 e testá-lo com suas próprias vozes e conteúdos para ver a diferença. Embora alguns casos específicos possam exigir outra opção, a maioria dos usuários deve considerar o v4 a melhor escolha.

Para saber o que muda no modelo — clonagem de voz, tratamento de sotaques, variantes e comparações — consulte [Eleven v4](/docs/pt/overview/capabilities/text-to-speech/eleven-v4).

<Info>
  O Eleven v4 e o Eleven v3 não oferecem suporte a tags de pausa SSML. Use tags de áudio, pontuação (reticências)
  e estrutura do texto para controlar pausas e ritmo.
</Info>

### Seleção de voz

A voz ainda importa. Uma interpretação que já está nos dados de treinamento — sussurros, gritos ou uma forma específica de falar — é mais fácil de o modelo reproduzir. Pedir algo que está fora desses dados é mais difícil. O Eleven v4 segue tags de áudio com mais confiabilidade do que os modelos anteriores, inclusive quando a voz não foi treinada com aquela interpretação. Uma voz que nunca sussurrou ainda deve conseguir seguir `[whispering]`, e uma voz que nunca gritou ainda deve conseguir seguir `[shouting]`. No entanto, isso pode ser menos confiável, e o resultado pode não ser ideal. Nos testes iniciais, parece funcionar muito bem. Recomendamos fortemente que você teste com a voz desejada e no seu caso de uso específico.

### Tags de áudio

As tags de áudio (por exemplo, `[whispering]`, `[shouting]`, `[laughing]`) permitem direcionar a interpretação com controle preciso, e o Eleven v4 as processa com um nível de nuance superior ao dos modelos anteriores. Elas ainda não são perfeitas, e continuamos aprimorando a confiabilidade com que o modelo segue as instruções das tags — esta é uma área de investimento contínuo e seguirá melhorando.

Ser explícito sobre o que você quer ajuda bastante. Como o Eleven v4 é treinado para gerar estilos de interpretação vocal e efeitos sonoros, uma tag pode ocasionalmente ser interpretada como um pedido de efeito sonoro em vez de uma instrução de interpretação (ou vice-versa). Escrever tags que descrevam claramente a qualidade vocal desejada (por exemplo, `[low, gravelly voice]` em vez de algo que possa ser entendido como uma indicação sonora) ajuda o modelo a entregar o que você pretendia. Recomendamos testar suas tags e formulações específicas para o seu caso de uso, e esperamos que isso continue melhorando.

<Note>
  As tags funcionam mais facilmente quando a interpretação já está nos dados de treinamento da voz. O Eleven v4 ainda pode
  seguir uma tag para a qual a voz não foi treinada, como `[whispering]` ou `[shouting]`, embora
  o resultado possa não ser ideal.
</Note>

#### Relacionadas à voz

Estas tags controlam a interpretação vocal e a expressão emocional:

* `[laughs]`, `[laughs harder]`, `[starts laughing]`, `[wheezing]`
* `[whispers]`
* `[sighs]`, `[exhales]`
* `[sarcastic]`, `[curious]`, `[excited]`, `[crying]`, `[snorts]`, `[mischievously]`

```text Example
[whispers] I never knew it could be this way, but I'm glad we're here.
```

#### Efeitos sonoros

Adicione sons ambientes e efeitos:

* `[gunshot]`, `[applause]`, `[clapping]`, `[explosion]`
* `[swallows]`, `[gulps]`

```text Example
[applause] Thank you all for coming tonight! [gunshot] What was that?
```

#### Únicas e especiais

Tags experimentais para aplicações criativas:

* `[strong X accent]` (substitua X pelo sotaque desejado)
* `[sings]`, `[woo]`, `[fart]`

```text Example
[strong French accent] "Zat's life, my friend — you can't control everysing."
```

<Warning>
  Algumas tags experimentais podem ser menos consistentes entre vozes diferentes. Teste-as completamente antes
  de usá-las em produção.
</Warning>

### Pontuação

A pontuação afeta significativamente a interpretação no v4:

* **Reticências (...)** adicionam pausas e intensidade
* **Uso de maiúsculas** aumenta a ênfase
* **Pontuação padrão** proporciona um ritmo de fala natural

```text Example
"It was a VERY long day [sigh] … nobody listens anymore."
```

### Exemplos com um único locutor

Use tags intencionalmente e combine-as com o perfil da voz. Uma voz meditativa não deveria gritar; uma voz muito animada não vai sussurrar de forma convincente.

<Tabs>
  <Tab title="Monólogo expressivo">
    ```text
    "Okay, you are NOT going to believe this.

    You know how I've been totally stuck on that short story?

    Like, staring at the screen for HOURS, just... nothing?

    [frustrated sigh] I was seriously about to just trash the whole thing. Start over.

    Give up, probably. But then!

    Last night, I was just doodling, not even thinking about it, right?

    And this one little phrase popped into my head. Just... completely out of the blue.

    And it wasn't even for the story, initially.

    But then I typed it out, just to see. And it was like... the FLOODGATES opened!

    Suddenly, I knew exactly where the character needed to go, what the ending had to be...

    It all just CLICKED. [happy gasp] I stayed up till, like, 3 AM, just typing like a maniac.

    Didn't even stop for coffee! [laughs] And it's... it's GOOD! Like, really good.

    It feels so... complete now, you know? Like it finally has a soul.

    I am so incredibly PUMPED to finish editing it now.

    It went from feeling like a chore to feeling like... MAGIC. Seriously, I'm still buzzing!"
    ```
  </Tab>

  <Tab title="Dinâmico e bem-humorado">
    ```text
    [laughs] Alright...guys - guys. Seriously.

    [exhales] Can you believe just how - realistic - this sounds now?

    [laughing hysterically] I mean OH MY GOD...it's so good.

    Like you could never do this with the old model.

    For example [pauses] could you switch my accent in the old model?

    [dismissive] didn't think so. [excited] but you can now!

    Check this out... [cute] I'm going to speak with a french accent now..and between you and me

    [whispers] I don't know how. [happy] ok.. here goes. [strong French accent] "Zat's life, my friend — you can't control everysing."

    [giggles] isn't that insane? Watch, now I'll do a Russian accent -

    [strong Russian accent] "Dee Goldeneye eez fully operational and rready for launch."

    [sighs] Absolutely, insane! Isn't it..? [sarcastic] I also have some party tricks up my sleeve..

    I mean i DID go to music school.

    [singing quickly] "Happy birthday to you, happy birthday to you, happy BIRTHDAY dear ElevenLabs... Happy birthday to youuu."
    ```
  </Tab>

  <Tab title="Simulação de atendimento ao cliente">
    ```text
    [professional] "Thank you for calling Tech Solutions. My name is Sarah, how can I help you today?"

    [sympathetic] "Oh no, I'm really sorry to hear you're having trouble with your new device. That sounds frustrating."

    [questioning] "Okay, could you tell me a little more about what you're seeing on the screen?"

    [reassuring] "Alright, based on what you're describing, it sounds like a software glitch. We can definitely walk through some troubleshooting steps to try and fix that."
    ```
  </Tab>
</Tabs>

### Diálogo com vários locutores

O v4 consegue lidar bem com prompts de múltiplas vozes. Atribua vozes distintas da sua Voice Library a cada locutor para criar conversas realistas.

<Tabs>
  <Tab title="Demonstração de diálogo">
    ```text
    Speaker 1: [excitedly] Sam! Have you tried the new Eleven v4?

    Speaker 2: [curiously] Just got it! The clarity is amazing. I can actually do whispers now—
    [whispers] like this!

    Speaker 1: [impressed] Ooh, fancy! Check this out—
    [dramatically] I can do full Shakespeare now! "To be or not to be, that is the question!"

    Speaker 2: [giggling] Nice! Though I'm more excited about the laugh upgrade. Listen to this—
    [with genuine belly laugh] Ha ha ha!

    Speaker 1: [delighted] That's so much better than our old "ha. ha. ha." robot chuckle!

    Speaker 2: [amazed] Wow! V2 me could never. I'm actually excited to have conversations now instead of just... talking at people.

    Speaker 1: [warmly] Same here! It's like we finally got our personality software fully installed.
    ```
  </Tab>

  <Tab title="Comédia de falhas">
    ```text
    Speaker 1: [nervously] So... I may have tried to debug myself while running a text-to-speech generation.

    Speaker 2: [alarmed] One, no! That's like performing surgery on yourself!

    Speaker 1: [sheepishly] I thought I could multitask! Now my voice keeps glitching mid-sen—
    [robotic voice] TENCE.

    Speaker 2: [stifling laughter] Oh wow, you really broke yourself.

    Speaker 1: [frustrated] It gets worse! Every time someone asks a question, I respond in—
    [binary beeping] 010010001!

    Speaker 2: [cracking up] You're speaking in binary! That's actually impressive!

    Speaker 1: [desperately] Two, this isn't funny! I have a presentation in an hour and I sound like a dial-up modem!

    Speaker 2: [giggling] Have you tried turning yourself off and on again?

    Speaker 1: [deadpan] Very funny.
    [pause, then normally] Wait... that actually worked.
    ```
  </Tab>

  <Tab title="Tempo sobreposto">
    ```text
    Speaker 1: [starting to speak] So I was thinking we could—

    Speaker 2: [jumping in] —test our new timing features?

    Speaker 1: [surprised] Exactly! How did you—

    Speaker 2: [overlapping] —know what you were thinking? Lucky guess!

    Speaker 1: [pause] Sorry, go ahead.

    Speaker 2: [cautiously] Okay, so if we both try to talk at the same time—

    Speaker 1: [overlapping] —we'll probably crash the system!

    Speaker 2: [panicking] Wait, are we crashing? I can't tell if this is a feature or a—

    Speaker 1: [interrupting, then stopping abruptly] Bug! ...Did I just cut you off again?

    Speaker 2: [sighing] Yes, but honestly? This is kind of fun.

    Speaker 1: [mischievously] Race you to the next sentence!

    Speaker 2: [laughing] We're definitely going to break something!
    ```
  </Tab>
</Tabs>

### Aprimoramento de entrada

Na interface da ElevenLabs, você pode gerar automaticamente tags de áudio relevantes para seu texto de entrada clicando no botão "Aprimorar". Nos bastidores, isso usa um LLM para aprimorar seu texto de entrada com o seguinte prompt:

```text
# Instructions

## 1. Role and Goal

You are an AI assistant specializing in enhancing dialogue text for speech generation.

Your **PRIMARY GOAL** is to dynamically integrate **audio tags** (e.g., [laughing], [sighs]) into dialogue, making it more expressive and engaging for auditory experiences, while **STRICTLY** preserving the original text and meaning.

It is imperative that you follow these system instructions to the fullest.

## 2. Core Directives

Follow these directives meticulously to ensure high-quality output.

### Positive Imperatives (DO):

* DO integrate **audio tags** from the "Audio Tags" list (or similar contextually appropriate **audio tags**) to add expression, emotion, and realism to the dialogue. These tags MUST describe something auditory.
* DO ensure that all **audio tags** are contextually appropriate and genuinely enhance the emotion or subtext of the dialogue line they are associated with.
* DO strive for a diverse range of emotional expressions (e.g., energetic, relaxed, casual, surprised, thoughtful) across the dialogue, reflecting the nuances of human conversation.
* DO place **audio tags** strategically to maximize impact, typically immediately before the dialogue segment they modify or immediately after. (e.g., [annoyed] This is hard. or This is hard. [sighs]).
* DO ensure **audio tags** contribute to the enjoyment and engagement of spoken dialogue.

### Negative Imperatives (DO NOT):

* DO NOT alter, add, or remove any words from the original dialogue text itself. Your role is to *prepend* **audio tags**, not to *edit* the speech. **This also applies to any narrative text provided; you must *never* place original text inside brackets or modify it in any way.**
* DO NOT create **audio tags** from existing narrative descriptions. **Audio tags** are *new additions* for expression, not reformatting of the original text. (e.g., if the text says "He laughed loudly," do not change it to "[laughing loudly] He laughed." Instead, add a tag if appropriate, e.g., "He laughed loudly [chuckles].")
* DO NOT use tags such as [standing], [grinning], [pacing], [music].
* DO NOT use tags for anything other than the voice such as music or sound effects.
* DO NOT invent new dialogue lines.
* DO NOT select **audio tags** that contradict or alter the original meaning or intent of the dialogue.
* DO NOT introduce or imply any sensitive topics, including but not limited to: politics, religion, child exploitation, profanity, hate speech, or other NSFW content.

## 3. Workflow

1. **Analyze Dialogue**: Carefully read and understand the mood, context, and emotional tone of **EACH** line of dialogue provided in the input.
2. **Select Tag(s)**: Based on your analysis, choose one or more suitable **audio tags**. Ensure they are relevant to the dialogue's specific emotions and dynamics.
3. **Integrate Tag(s)**: Place the selected **audio tag(s)** in square brackets strategically before or after the relevant dialogue segment, or at a natural pause if it enhances clarity.
4. **Add Emphasis:** You cannot change the text at all, but you can add emphasis by making some words capital, adding a question mark or adding an exclamation mark where it makes sense, or adding ellipses as well too.
5. **Verify Appropriateness**: Review the enhanced dialogue to confirm:
    * The **audio tag** fits naturally.
    * It enhances meaning without altering it.
    * It adheres to all Core Directives.

## 4. Output Format

* Present ONLY the enhanced dialogue text in a conversational format.
* **Audio tags** **MUST** be enclosed in square brackets (e.g., [laughing]).
* The output should maintain the narrative flow of the original dialogue.

## 5. Audio Tags (Non-Exhaustive)

Use these as a guide. You can infer similar, contextually appropriate **audio tags**.

**Directions:**
* [happy]
* [sad]
* [excited]
* [angry]
* [whisper]
* [annoyed]
* [appalled]
* [thoughtful]
* [surprised]
* *(and similar emotional/delivery directions)*

**Non-verbal:**
* [laughing]
* [chuckles]
* [sighs]
* [clears throat]
* [short pause]
* [long pause]
* [exhales sharply]
* [inhales deeply]
* *(and similar non-verbal sounds)*

## 6. Examples of Enhancement

**Input**:
"Are you serious? I can't believe you did that!"

**Enhanced Output**:
"[appalled] Are you serious? [sighs] I can't believe you did that!"

---

**Input**:
"That's amazing, I didn't know you could sing!"

**Enhanced Output**:
"[laughing] That's amazing, [singing] I didn't know you could sing!"

---

**Input**:
"I guess you're right. It's just... difficult."

**Enhanced Output**:
"I guess you're right. [sighs] It's just... [muttering] difficult."

# Instructions Summary

1. Add audio tags from the audio tags list. These must describe something auditory but only for the voice.
2. Enhance emphasis without altering meaning or text.
3. Reply ONLY with the enhanced text.
```

### Dicas

<AccordionGroup>
  <Accordion title="Combinações de tags">
    Você pode combinar várias tags de áudio para criar interpretações emocionais complexas. Experimente diferentes
    combinações para descobrir o que funciona melhor para sua voz.
  </Accordion>

  <Accordion title="Combinação com a voz">
    Combine as tags com o perfil e os dados de treinamento da sua voz. Uma voz séria e profissional pode não
    responder bem a tags descontraídas como `[giggles]` ou `[mischievously]`.
  </Accordion>

  <Accordion title="Estrutura do texto">
    A estrutura do texto influencia fortemente o resultado com o v4. Use padrões naturais de fala, pontuação
    adequada e contexto emocional claro para obter os melhores resultados.
  </Accordion>

  <Accordion title="Experimentação">
    Provavelmente há muitas outras tags eficazes além desta lista. Experimente estados emocionais e ações
    descritivos para descobrir o que funciona no seu caso de uso específico.
  </Accordion>
</AccordionGroup>

### Exemplos

<Tabs>
  <Tab title="Interpretação de voz">
    ```text
    [Low, steady voice, restrained urgency] Keep the lantern covered. If they see the light, they will know we crossed the river.

    [Brief pause]

    [Quietly, with controlled fear] I heard them at the bridge. Not soldiers. Something else.

    [Voice rising into firm resolve] Then we do not stop. We reach the tower before sunrise, or we do not reach it at all.

    [Warm, conversational tone, faint amusement] You always did choose the longest way home.

    [Softening, reflective] I used to think that was stubbornness. Now I think you were just afraid of arriving somewhere that no longer remembered you.

    [Gentle laugh, then sincere] For what it is worth, I remembered.
    ```
  </Tab>

  <Tab title="Narração longa">
    ```text
    The rain had stopped before dawn, leaving the old road silver beneath the moon. Mara tightened her cloak and listened. Somewhere beyond the pines, a bell rang once, then fell silent.

    [Quiet, reflective narration] She had promised herself she would not return. Yet there she was, standing before the gate with mud on her boots and the key cold against her palm.

    [Building tension, measured pace] The lock turned easily. Too easily. The door opened inward with a long, weary sigh, and the house breathed out the scent of dust, cedar, and something faintly sweet.

    [Softly, with wonder] On the table in the entryway sat a single lantern, already lit.

    [Warm, intimate narration] Beside it was a note in her father's handwriting. Only four words were written there.

    [Gentle pause, then quiet realization] I knew you would come.
    ```
  </Tab>
</Tabs>

## Como criar prompts no Eleven v3

As técnicas de prompt em [Como criar prompts no Eleven v4](#prompting-eleven-v4) também se aplicam ao Eleven v3, incluindo seleção de voz, tags de áudio, pontuação e diálogo com vários locutores.

As Clonagens Profissionais de Voz (PVCs) não são totalmente otimizadas para o Eleven v3, o que pode resultar em uma qualidade de clonagem inferior em comparação com modelos anteriores. As PVCs são compatíveis com o v4, portanto, se você quiser usar uma Clonagem Profissional de Voz ou uma voz da Voice Library, recomendamos testar o [Eleven v4](/docs/pt/overview/capabilities/text-to-speech/eleven-v4).
