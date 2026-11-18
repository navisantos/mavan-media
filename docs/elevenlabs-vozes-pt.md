---

title: Vozes
subtitle: Saiba como criar, personalizar e gerenciar vozes com a ElevenLabs.
----------------------------------------------------------------------------

## Visão geral

A ElevenLabs oferece modelos para criação e personalização de vozes. A plataforma oferece uma ampla variedade de opções de voz, incluindo vozes da nossa extensa [Voice Library](https://elevenlabs.io/app/voice-library), clonagem de voz e vozes geradas a partir de prompts de texto.

### Tipos de voz

* **Comunidade**: Vozes compartilhadas pela comunidade na [Voice Library](/docs/pt/eleven-creative/voices/voice-library) da ElevenLabs.
* **Clonadas**: Vozes personalizadas criadas com Instant Voice Cloning ou Professional Voice Cloning.
* **Voice Design**: Vozes geradas com a ferramenta [Voice Design](/docs/pt/eleven-creative/voices/voice-design).

<Warning>
  Nossas vozes padrão estão sendo substituídas por novas vozes que você poderá usar permanentemente.
  Todas as nossas vozes padrão expirarão em 31 de dezembro de 2026 e não estarão mais acessíveis
  após essa data.
</Warning>

#### Comunidade

A [Voice Library](/docs/pt/eleven-creative/voices/voice-library) contém mais de 10.000 vozes compartilhadas pela comunidade da ElevenLabs. Use-a para:

* Descobrir vozes únicas compartilhadas pela comunidade da ElevenLabs.
* Adicionar vozes à sua coleção pessoal.
* Compartilhar seus próprios clones de voz e receber recompensas em dinheiro quando outros assinantes pagos os usarem.

<Success>
  Compartilhe sua voz com a comunidade, defina seus termos e receba recompensas em dinheiro quando outras pessoas a usarem.
  Já pagamos mais de **US\$ 14 milhões**.
</Success>

<Warning>
  As vozes da Voice Library não estão disponíveis via API para usuários do plano gratuito.
</Warning>

<CardGroup cols={1}>
  <Card title="Produtos" icon="duotone book-user" iconPosition="left" href="/docs/pt/eleven-creative/voices/voice-library">
    Saiba como usar vozes da Voice Library
  </Card>
</CardGroup>

#### Clonadas

Clone sua própria voz a partir de amostras curtas de áudio com o Instant Voice Cloning ou crie vozes realistas usando o Professional Voice Cloning.

* **Instant Voice Cloning**: Clone rapidamente uma voz a partir de amostras curtas de áudio.
* **Professional Voice Cloning**: Gere clones de voz com qualidade profissional usando áudio de treinamento mais extenso.

A tecnologia de captcha de voz é usada para verificar se os Professional Voice Clones são criados com suas próprias amostras de voz.

<Note>
  É necessário ter um plano Creator ou superior para criar Professional Voice Clones.
</Note>

<CardGroup cols={2}>
  <Card title="Produtos" icon="duotone book-user" iconPosition="left" href="/docs/pt/eleven-creative/voices/voice-cloning">
    Saiba como criar Instant Voice Cloning e Professional Voice Cloning
  </Card>

  <Card title="Instant Voice Cloning" icon="duotone code" href="/docs/pt/eleven-api/guides/how-to/voices/instant-voice-cloning">
    Clone uma voz instantaneamente
  </Card>

  <Card title="Professional Voice Cloning" icon="duotone code" href="/docs/pt/eleven-api/guides/how-to/voices/professional-voice-cloning">
    Crie um clone de voz realista
  </Card>
</CardGroup>

#### Voice Design

Com o [Voice Design](/docs/pt/eleven-creative/voices/voice-design), você pode criar vozes totalmente novas especificando atributos como idade, gênero, sotaque e tom. As vozes geradas são ideais para:

* Vozes realistas com características detalhadas.
* Vozes criativas de personagens para jogos e narrativas.

O Voice Design cria 3 prévias de voz. Basta fornecer:

* Uma **descrição da voz** entre 20 e 1.000 caracteres.
* Um **texto** opcional para visualizar a voz, entre 100 e 1.000 caracteres.

##### Voice Design com Eleven v4

O [Eleven v4](/docs/pt/overview/capabilities/text-to-speech/eleven-v4) é o modelo a usar. As vozes do Voice Design funcionam com ele, embora possam ter desempenho inferior ao obtido com modelos anteriores. O Eleven v3 também pode criar vozes com uma ampla variedade de emoções.

O uso desses modelos traz os seguintes benefícios:

* Geração de voz mais natural e versátil.
* Mais controle sobre as características da voz.
* Tags de áudio compatíveis em gerações de prévia.
* Compatibilidade retroativa com modelos v2.

<CardGroup cols={2}>
  <Card title="Produtos" icon="duotone book-user" href="/docs/pt/eleven-creative/voices/voice-design">
    Saiba como criar vozes a partir de um único prompt.
  </Card>

  <Card title="Desenvolvedores" icon="duotone code" href="/docs/pt/eleven-api/guides/how-to/voices/voice-design">
    Integre o Voice Design ao seu aplicativo.
  </Card>
</CardGroup>

#### Remixagem de voz

A Remixagem de Voz permite transformar vozes que você possui modificando seus atributos principais e mantendo suas características reconhecíveis. Você pode ajustar o gênero, sotaque, estilo de fala, ritmo e qualidade de áudio por meio de prompts em linguagem natural. Esse recurso é especialmente útil para adaptar vozes a diferentes contextos, criar variações de personagens ou melhorar a qualidade de áudio de perfis de voz existentes. A Remixagem de Voz funciona com qualquer voz clonada que você possua pessoalmente (Instant Voice Cloning ou Professional Voice Cloning) ou vozes criadas com o Voice Design.

<CardGroup cols={2}>
  <Card title="Produtos" icon="duotone book-user" href="/docs/pt/overview/capabilities/voice-remixing">
    Saiba como transformar e aprimorar vozes
  </Card>

  <Card title="Desenvolvedores" icon="duotone code" href="/docs/pt/eleven-api/guides/how-to/voices/remix-a-voice">
    Integre a Remixagem de Voz ao seu aplicativo
  </Card>
</CardGroup>

### Gerenciando vozes

Todas as vozes podem ser gerenciadas em [**Minhas vozes**](https://elevenlabs.io/app/voice-lab), onde você pode:

* Pesquisar, filtrar e categorizar vozes
* Adicionar descrições e tags personalizadas
* Organizar vozes para acesso rápido

Saiba como gerenciar sua coleção de vozes na [documentação de Minhas vozes](/docs/pt/eleven-creative/voices/voice-library#my-voices).

* **Pesquisar e filtrar**: Encontre vozes usando palavras-chave ou tags.
* **Visualizar amostras**: Ouça demonstrações de voz antes de usá-las.
* **Adicionar à coleção**: Salve vozes para acessá-las facilmente em seus projetos.

> **Dica**: Tente pesquisar por sotaques ou gêneros específicos, como "narração australiana".

### Idiomas compatíveis

Todas as vozes da ElevenLabs são compatíveis com vários idiomas. A ElevenLabs oferece criação de voz em 32 idiomas. Escolha uma voz que corresponda à sua região de destino para obter resultados mais naturais.

* **Vozes geradas e clonadas**: A fidelidade do sotaque depende das amostras de entrada ou dos atributos selecionados.

Nossos modelos multilíngues v2 oferecem suporte a 29 idiomas:

*Inglês (EUA, Reino Unido, Austrália, Canadá), Japonês, Chinês, Alemão, Hindi, Francês (França, Canadá), Coreano, Português (Brasil, Portugal), Italiano, Espanhol (Espanha, México), Indonésio, Holandês, Turco, Filipino, Polonês, Sueco, Búlgaro, Romeno, Árabe (Arábia Saudita, Emirados Árabes Unidos), Tcheco, Grego, Finlandês, Croata, Malaio, Eslovaco, Dinamarquês, Tâmil, Ucraniano e Russo.*

O Flash v2.5 oferece suporte a 32 idiomas — todos os idiomas dos modelos v2, além de:

*Húngaro, Norueguês e Vietnamita*

[Saiba mais sobre nossos modelos](/docs/pt/overview/models)

## Informações principais

* **Instant Voice Cloning**: Criado a partir de amostras curtas de áudio (menos de dois minutos); disponível na maioria dos planos
* **Professional Voice Cloning**: Requer áudio de treinamento mais extenso para maior fidelidade; requer um plano Creator ou superior
* **Compartilhamento de voz**: Professional Voice Clones podem ser compartilhados publicamente na Voice Library; Instant Voice Clones e Generated Voices não podem
* **Vozes geradas**: Criadas a partir de descrições de texto pelo Voice Design — ideais para personagens únicos em jogos, animações e narrativas criativas
