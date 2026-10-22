# Atividade 4 - Comunicação Modbus TCP com Emulação de CLP

**Disciplina:** ENE118 – Informática Industrial
**Instituição:** Universidade Federal de Juiz de Fora (UFJF) 
## Integrantes e Divisão de Responsabilidades
- **Guilherme de Almeida Paula**: Implementação do Cliente Modbus (leitura/escrita de float e bits, escalas) e scripts de demonstração.
- **Henrique Brandão Bairral Muniz**: Implementação do Servidor Modbus (emulação do CLP, mapa de registradores, simulação do processo físico).

## Instalação e Execução
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie o servidor (em um terminal, a partir da raiz do projeto):
   ```bash
   python servidor/servidor_modbus.py
   ```
   *Servidor configurado para rodar em `127.0.0.1` na porta `5020`.
3. Execute as demonstrações (em outro terminal, a partir da raiz do projeto):
   ```bash
   python exemplos/exemplo_escala.py
   python exemplos/exemplo_float.py
   python exemplos/exemplo_bits.py
   ```

## Comportamento da Simulação
O servidor emula uma bancada de bombeamento. O sistema depende do comando de habilitação do motor, controlado pelo bit 6 do registrador 1328. 
- **Motor Habilitado (Bit 6 = 1):** A vazão simulada (`bc.fit01`) aproxima-se gradualmente do setpoint de vazão (`bc.sp_pid`), acrescida de um leve ruído aleatório. Variáveis dependentes como pressão, frequência, corrente e temperaturas aumentam de forma proporcional à vazão e à operação do equipamento.
- **Motor Desabilitado (Bit 6 = 0):** A vazão decai exponencialmente para zero. Frequência, corrente e pressão caem para zero, enquanto as temperaturas retornam aos seus valores base.

## Mapa de Dados
O mapa contém 12 variáveis no total: 10 medições de leitura, 1 setpoint de escrita e 1 registrador de comando por bit.

| Tag / Dado | Descrição | Tipo | Endereço | Quantidade | Bit | Div (D) | Mult (m) | Unidade |
|---|---|---|---|---|---|---|---|---|
| `bc.temp_r` | Temperatura R | FP | 700-701 | 2 | - | 10 | 0.1 | °C |
| `bc.temp_s` | Temperatura S | FP | 702-703 | 2 | - | 10 | 0.1 | °C |
| `bc.temp_t` | Temperatura T | FP | 704-705 | 2 | - | 10 | 0.1 | °C |
| `bc.temp_carc` | Temperatura Carcaça | FP | 706-707 | 2 | - | 10 | 0.1 | °C |
| `bc.pit01` | Pressão | FP | 710-711 | 2 | - | 1 | 1 | bar |
| `bc.fit01` | Vazão | FP | 712-713 | 2 | - | 1 | 1 | L/min |
| `bc.frequencia` | Frequência | 4X | 830 | 1 | - | 100 | 0.01 | Hz |
| `bc.corrente_r` | Corrente R | 4X | 840 | 1 | - | 10 | 0.1 | A |
| `bc.tensao_rs` | Tensão R-S | 4X | 847 | 1 | - | 10 | 0.1 | V |
| `bc.fp_r` | Fator de Potência R | 4X | 868 | 1 | - | 1000 | 0.001 | - |
| `bc.sp_pid` | Setpoint de Vazão | FP | 1302-1303 | 2 | - | 1 | 1 | L/min |
| `bc.habilita` | Habilitar Motor | 4X/bit | 1328 | 1 | 6 | 1 | 1 | - |

*Fonte do mapa base: Roteiro da atividade*

## Detalhes Técnicos e Padrões Adotados
- **Ordem de Palavras e Bytes (Float32):** Para a representação dos valores de ponto flutuante (FP) em dois registradores de 16 bits consecutivos, foi adotado o padrão **Big Endian** tanto para a ordem dos bytes quanto para a ordem das palavras.
- **Conversão de Escala:** 
  - Na **leitura**, o cliente divide o valor numérico cru recebido pelo fator Divisor (ou multiplica pelo multiplicador `m`) para obter o valor de engenharia.
  - Na **escrita**, o cliente multiplica o valor de engenharia desejado pelo fator Divisor antes de codificá-lo e enviá-lo para os registradores do servidor.
