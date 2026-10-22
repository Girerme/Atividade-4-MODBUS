import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cliente.cliente_modbus import ClienteMODBUS

def main():
    cliente = ClienteMODBUS('127.0.0.1', 5020)
    if not cliente.conectar():
        print("Erro: Não foi possível estabelecer conexão ao servidor Modbus.")
        return

    print("=== Demonstração: Escrita e Leitura de Float ===")
    
    addr_sp = 1302
    div = 1
    
    setpoint_engenharia = 42.5
    
    valor_enviado = setpoint_engenharia * div
    
    print(f"Enviando Setpoint: {setpoint_engenharia} L/min (Valor Cru enviado: {valor_enviado}) para os registos {addr_sp}-{addr_sp+1}...")
    sucesso = cliente.escreve_float(addr_sp, valor_enviado)
    
    if sucesso:
        print("Escrita realizada com sucesso. Aguardando atualização do servidor...")
        time.sleep(1)
        
        valor_lido_cru = cliente.ler_float(addr_sp)
        if valor_lido_cru is not None:
            valor_lido_eng = valor_lido_cru / div
            print(f"Valor lido (Cru): {valor_lido_cru:.4f}")
            print(f"Valor recuperado em Engenharia: {valor_lido_eng:.4f} L/min")
        else:
            print("Falha ao ler o float do servidor.")
    else:
        print("Falha na escrita do float.")

    cliente.desconectar()

if __name__ == '__main__':
    main()