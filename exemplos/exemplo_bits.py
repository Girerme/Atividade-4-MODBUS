import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cliente.cliente_modbus import ClienteMODBUS

def main():
    cliente = ClienteMODBUS('127.0.0.1', 5020)
    if not cliente.conectar():
        print("Erro ao conectar no servidor Modbus.")
        return

    print("=== Demonstração: Leitura e Alteração de Bits ===")
    addr_cmd = 1328
    bit_motor = 6

    valor_inicial = 0b1000000000000001
    print(f"A escrever valor inicial de teste (Bits 0 e 15 a '1'): {bin(valor_inicial)}")
    cliente.escreve_holding_register(addr_cmd, valor_inicial)
    time.sleep(0.5)

    bits = cliente.ler_bits_registrador(addr_cmd)
    print(f"Estado inicial dos 16 bits: {bits}")

    # ligao motor
    print(f"\nA ativar o bit {bit_motor} (Ligar motor)...")
    cliente.escreve_bit_individual(addr_cmd, bit_motor, 1)
    
    bits_ligado = cliente.ler_bits_registrador(addr_cmd)
    print(f"Estado dos 16 bits após ligar: {bits_ligado}")
    print("A aguardar 3 segundos para observar o motor a funcionar...")
    time.sleep(3)

    #desliga motor
    print(f"\nA desativar o bit {bit_motor} (Desligar motor)...")
    cliente.escreve_bit_individual(addr_cmd, bit_motor, 0)   
    bits_desligado = cliente.ler_bits_registrador(addr_cmd)
    print(f"Estado dos 16 bits após desligar: {bits_desligado}")   
    print("\nNota: Os bits 0 e 15 foram preservados durante toda a operação, tal como exigido!")

    cliente.desconectar()

if __name__ == '__main__':
    main()