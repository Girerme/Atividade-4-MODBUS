import time
import random
import struct
from pyModbusTCP.server import ModbusServer

def float_to_registers(val: float):
    raw_bytes = struct.pack('>f', val)
    reg1, reg2 = struct.unpack('>HH', raw_bytes)
    return [reg1, reg2]

def registers_to_float(regs: list):
    raw_bytes = struct.pack('>HH', regs[0], regs[1])
    return struct.unpack('>f', raw_bytes)[0]

def main():
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5020

    server = ModbusServer(host=SERVER_IP, port=SERVER_PORT, no_block=True)
    
    print(f"Iniciando Servidor Modbus TCP em {SERVER_IP}:{SERVER_PORT}...")
    server.start()
    print("Servidor rodando e aguardando conexões do cliente.\n")

    server.data_bank.set_holding_registers(1302, float_to_registers(50.0))
    server.data_bank.set_holding_registers(1328, [0])

    vazao_simulada = 0.0

    try:
        while True:
            sp_regs = server.data_bank.get_holding_registers(1302, 2)
            setpoint_vazao = registers_to_float(sp_regs) if sp_regs else 0.0

            cmd_regs = server.data_bank.get_holding_registers(1328, 1)
            cmd_reg = cmd_regs[0] if cmd_regs else 0
            motor_habilitado = bool((cmd_reg >> 6) & 0x01)

            if motor_habilitado:
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

            #float
            server.data_bank.set_holding_registers(700, float_to_registers(temp_base * 10))
            server.data_bank.set_holding_registers(702, float_to_registers((temp_base + 0.2) * 10))
            server.data_bank.set_holding_registers(704, float_to_registers((temp_base - 0.3) * 10))
            server.data_bank.set_holding_registers(706, float_to_registers((temp_base + 10) * 10))
            server.data_bank.set_holding_registers(710, float_to_registers(pressao_bar * 1))
            server.data_bank.set_holding_registers(712, float_to_registers(vazao_simulada * 1))

            #int
            server.data_bank.set_holding_registers(830, [int(frequencia_hz * 100)])
            server.data_bank.set_holding_registers(840, [int(corrente_a * 10)])
            server.data_bank.set_holding_registers(847, [int(220.0 * 10)])
            server.data_bank.set_holding_registers(868, [int(0.95 * 1000)])

            time.sleep(1)

    except KeyboardInterrupt:
        server.stop()
        print("\nServidor Modbus finalizado com sucesso.")

if __name__ == '__main__':
    main()