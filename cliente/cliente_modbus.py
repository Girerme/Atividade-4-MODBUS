from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian

class ClienteMODBUS:
    """Classe Cliente MODBUS exclusiva para comunicação e conversão de dados."""
    
    def __init__(self, server_ip, porta):
        self._cliente = ModbusTcpClient(host=server_ip, port=porta)
        self.byte_order = Endian.BIG
        self.word_order = Endian.BIG

    def conectar(self):
        return self._cliente.connect()

    def desconectar(self):
        self._cliente.close()

    def ler_holding_register(self, addr):
        """Lê um Holding Register inteiro (16 bits)."""
        resp = self._cliente.read_holding_registers(address=addr, count=1, slave=1)
        if resp and not resp.isError():
            return resp.registers[0]
        return None

    def escreve_holding_register(self, addr, valor):
        """Escreve um valor inteiro em um Holding Register."""
        resp = self._cliente.write_register(address=addr, value=int(valor), slave=1)
        return bool(resp and not resp.isError())

    def ler_float(self, addr):
        """Lê um valor float32 em dois Holding Registers consecutivos."""
        resp = self._cliente.read_holding_registers(address=addr, count=2, slave=1)
        if resp and not resp.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                resp.registers, byteorder=self.byte_order, wordorder=self.word_order
            )
            return decoder.decode_32bit_float()
        return None

    def escreve_float(self, addr, valor):
        """Escreve um valor float32 ocupando dois Holding Registers consecutivos."""
        builder = BinaryPayloadBuilder(byteorder=self.byte_order, wordorder=self.word_order)
        builder.add_32bit_float(float(valor))
        payload = builder.to_registers()
        
        resp = self._cliente.write_registers(address=addr, values=payload, slave=1)
        return bool(resp and not resp.isError())

    def ler_bits_registrador(self, addr):
        """Retorna o estado dos 16 bits de um Holding Register (bit 0 = menos significativo)."""
        valor = self.ler_holding_register(addr)
        if valor is not None:
            return [(valor >> i) & 1 for i in range(16)]
        return None

    def escreve_bit_individual(self, addr, bit_index, valor_bit):
        """Altera um bit específico (0-15) de um registrador, preservando os demais."""
        if not (0 <= bit_index <= 15):
            raise ValueError("Índice do bit deve estar entre 0 e 15.")
        
        valor_atual = self.ler_holding_register(addr)
        if valor_atual is None:
            return False

        if valor_bit:
            novo_valor = valor_atual | (1 << bit_index)
        else:
            novo_valor = valor_atual & ~(1 << bit_index)

        return self.escreve_holding_register(addr, novo_valor)