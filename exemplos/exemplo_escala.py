import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cliente.cliente_modbus import ClienteMODBUS

def main():
    cliente = ClienteMODBUS('127.0.0.1', 5020)
    if not cliente.conectar():
        print("Erro: Não foi possível estabelecer conexão ao servidor Modbus.")
        return

    print("=== Demonstração: Leitura de Medições e Escala (10 dados) ===")
    
    print("\n-- Dados Inteiros --")
    dados_int = [
        ("bc.frequencia", 830, 100, 0.01, "Hz"),
        ("bc.corrente_r", 840, 10, 0.1, "A"),
        ("bc.tensao_rs", 847, 10, 0.1, "V"),
        ("bc.fp_r", 868, 1000, 0.001, "")
    ]
    for tag, addr, div, mult, unit in dados_int:
        val_cru = cliente.ler_holding_register(addr)
        if val_cru is not None:
            val_eng = val_cru * mult 
            print(f"{tag} (Endereço {addr}): Valor Cru={val_cru} | Div={div} | Mult={mult} | Eng={val_eng:.2f} {unit}")
            
    print("\n-- Dados Float32 --")
    dados_float = [
        ("bc.temp_r", 700, 10, 0.1, "°C"),
        ("bc.temp_s", 702, 10, 0.1, "°C"),
        ("bc.temp_t", 704, 10, 0.1, "°C"),
        ("bc.temp_carc", 706, 10, 0.1, "°C"),
        ("bc.pit01", 710, 1, 1, "bar"),
        ("bc.fit01", 712, 1, 1, "L/min")
    ]
    for tag, addr, div, mult, unit in dados_float:
        val_cru = cliente.ler_float(addr)
        if val_cru is not None:
            val_eng = val_cru * mult
            print(f"{tag} (Endereços {addr}-{addr+1}): Valor Cru={val_cru:.2f} | Div={div} | Mult={mult} | Eng={val_eng:.2f} {unit}")

    cliente.desconectar()

if __name__ == '__main__':
    main()