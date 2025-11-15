# Chat CMD - Terminal WebSocket Chat Client

Cliente de chat via WebSocket com suporte a imagens no terminal.

## Nova Estrutura do Projeto

```
chat-cmd/
├── app.py                          # Ponto de entrada principal
├── server.py                       # Servidor WebSocket
├── image.py                        # (DEPRECATED - usar src/utils/image_utils.py)
├── sounds/                         # Pasta de sons de notificação
└── src/                           # Código-fonte modular
    ├── __init__.py
    ├── core/                      # Módulos principais
    │   ├── __init__.py
    │   ├── config.py              # Configurações e constantes
    │   └── client.py              # Lógica do cliente WebSocket
    ├── handlers/                  # Manipuladores de eventos
    │   ├── __init__.py
    │   ├── message_handler.py     # Recepção/envio de mensagens
    │   └── command_handler.py     # Processamento de comandos
    └── utils/                     # Utilitários
        ├── __init__.py
        ├── image_utils.py         # Display de imagens no terminal
        └── sound.py               # Notificações sonoras
```

## Descrição dos Módulos

### `src/core/`
- **`config.py`**: Contém todas as configurações, constantes e o URI do WebSocket
- **`client.py`**: Gerencia a conexão WebSocket e a comunicação cliente-servidor

### `src/handlers/`
- **`message_handler.py`**: Processa mensagens recebidas (texto, imagens, notificações)
- **`command_handler.py`**: Processa comandos do usuário (/quit, /help, /image, /sound)

### `src/utils/`
- **`image_utils.py`**: Funções para exibir imagens no terminal usando ANSI codes
- **`sound.py`**: Gerencia notificações sonoras (WAV e MP3)

## Uso

Execute o cliente:
```bash
python app.py
```

Com som customizado:
```bash
python app.py --sound sounds/notification.wav
```

## Comandos Disponíveis

- `/quit` - Sair do chat
- `/help` - Mostrar lista de comandos
- `/image <caminho>` - Enviar e exibir imagem
- `/sound <caminho>` - Alterar som de notificação

## Benefícios da Nova Estrutura

1. **Modularidade**: Código organizado por responsabilidade
2. **Manutenibilidade**: Mais fácil de entender e modificar
3. **Testabilidade**: Módulos podem ser testados independentemente
4. **Escalabilidade**: Fácil adicionar novos comandos e funcionalidades
5. **Reusabilidade**: Utilitários podem ser usados em outros projetos
