import time
import random
import struct
from pyModbusTCP.server import ModbusServer, DataBank

def float_to_registers(val: float):
    """
    Converte um número float32 (4 bytes) em dois Holding Registers de 16 bits.
    Ordem de palavras: Big Endian (Word Order = BIG, Byte Order = BIG).
    """
    raw_bytes = struct.pack('>f', val)
    reg1, reg2 = struct.unpack('>HH', raw_bytes)
    return [reg1, reg2]

def registers_to_float(regs: list):
    """
    Converte dois Holding Registers de 16 bits de volta para um float32.
    """
    raw_bytes = struct.pack('>HH', regs[0], regs[1])
    return struct.unpack('>f', raw_bytes)[0]

def main():
    # Endereço IP e porta para conexão interna/local
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5020

    server = ModbusServer(host=SERVER_IP, port=SERVER_PORT, no_block=True)
    
    print(f"Iniciando Servidor Modbus TCP em {SERVER_IP}:{SERVER_PORT}...")
    server.start()
    print("Servidor rodando e aguardando conexões do cliente.\n")

    # Setpoint Inicial em 1302-1303: 50.0 L/min (Float, D=1)
    DataBank.set_words(1302, float_to_registers(50.0))
    
    # Registrador de Comando 1328 zerado (Bit 6 = 0, Desabilitado)
    DataBank.set_words(1328, [0])

    # Estado interno simulado
    vazao_simulada = 0.0

    try:
        while True:
            # Lê o Setpoint de Vazão nos registradores 1302-1303
            sp_regs = DataBank.get_words(1302, 2)
            setpoint_vazao = registers_to_float(sp_regs)

            # Lê o registrador de comandos (1328) e extrai o estado do bit 6 (bc.habilita)
            cmd_reg = DataBank.get_words(1328, 1)[0]
            motor_habilitado = bool((cmd_reg >> 6) & 0x01)

            if motor_habilitado:
                # Aproximação gradual da vazão ao setpoint com ruído
                vazao_simulada += (setpoint_vazao - vazao_simulada) * 0.15 + random.uniform(-0.1, 0.1)
                frequencia_hz = 60.0 + random.uniform(-0.2, 0.2)
                corrente_a = 12.5 + random.uniform(-0.3, 0.3)
                pressao_bar = 2.5 + (vazao_simulada * 0.02) + random.uniform(-0.05, 0.05)
                temp_base = 25.0 + (vazao_simulada * 0.1)
            else:
                vazao_simulada *= 0.8
                if vazao_simulada < 0.01:
                    vazao_simulada = 0.0
                frequencia_hz = 0.0
                corrente_a = 0.0
                pressao_bar = 0.0
                temp_base = 25.0

            # Dados Float (FP) com Escala Aplicada (Valor Armazenado = Valor Eng. x Div)
            DataBank.set_words(700, float_to_registers(temp_base * 10))        # bc.temp_r (D=10)
            DataBank.set_words(702, float_to_registers((temp_base + 0.2) * 10))# bc.temp_s (D=10)
            DataBank.set_words(704, float_to_registers((temp_base - 0.3) * 10))# bc.temp_t (D=10)
            DataBank.set_words(706, float_to_registers((temp_base + 10) * 10)) # bc.temp_carc (D=10)
            DataBank.set_words(710, float_to_registers(pressao_bar * 1))       # bc.pit01 (D=1)
            DataBank.set_words(712, float_to_registers(vazao_simulada * 1))    # bc.fit01 (D=1)

            # Dados Inteiros (4X) com Escala Aplicada (Valor Armazenado = Valor Eng. x Div)
            DataBank.set_words(830, [int(frequencia_hz * 100)]) # bc.frequencia (D=100)
            DataBank.set_words(840, [int(corrente_a * 10)])    # bc.corrente_r (D=10)
            DataBank.set_words(847, [int(220.0 * 10)])         # bc.tensao_rs (D=10)
            DataBank.set_words(868, [int(0.95 * 1000)])        # bc.fp_r (D=1000)

            time.sleep(1)

    except KeyboardInterrupt:
        server.stop()
        print("\nServidor Modbus finalizado com sucesso.")

if __name__ == '__main__':
    main()