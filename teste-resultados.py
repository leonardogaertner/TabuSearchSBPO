import os
import time
import pandas as pd
from main import Instance, tabu_search

# Caminho das instâncias
INSTANCIA_DIR = r"C:\Users\leonardo.gaertner\Desktop\Tabu\Instancias"
INSTANCIA_PREFIX = "instance_"
INSTANCIA_SUFFIX = ".txt"

# Parâmetros fixos para essa execução
TABU_TENURE = 115
MAX_ITERATIONS = 250
NEIGHBORHOOD_SIZE = 20
TIME_LIMIT = 300  # segundos

# Instâncias que você quer testar (15 a 20)
INSTANCIAS_TESTE = range(15, 21)

# Lista para armazenar resultados
resultados = []

def executar_instancias():
    for i in INSTANCIAS_TESTE:
        nome_arquivo = f"{INSTANCIA_PREFIX}{str(i).zfill(4)}{INSTANCIA_SUFFIX}"
        caminho = os.path.join(INSTANCIA_DIR, nome_arquivo)
        
        try:
            instancia = Instance.read_instance(caminho)
        except Exception as e:
            print(f"Erro ao carregar a instância {nome_arquivo}: {e}")
            continue

        print(f"\nExecutando instância {nome_arquivo}...")

        inicio = time.time()
        solucao = tabu_search(instancia,
                              time_limit=TIME_LIMIT,
                              tabu_tenure=TABU_TENURE,
                              max_iterations=MAX_ITERATIONS,
                              neighborhood_size=NEIGHBORHOOD_SIZE)
        fim = time.time()

        if solucao.orders:
            resultados.append({
                "Instância": nome_arquivo,
                "Tempo (s)": round(fim - inicio, 2),
                "Objetivo": solucao.objective,
                "Nº Pedidos": len(solucao.orders),
                "Nº Corredores": len(solucao.aisles)
            })
        else:
            print(f"Instância {nome_arquivo} não encontrou solução viável.")
            resultados.append({
                "Instância": nome_arquivo,
                "Tempo (s)": round(fim - inicio, 2),
                "Objetivo": None,
                "Nº Pedidos": 0,
                "Nº Corredores": 0
            })

def main():
    executar_instancias()
    df = pd.DataFrame(resultados)
    df.to_excel("resultados_execucao_unica.xlsx", index=False)
    print("\nResultados salvos em 'resultados_execucao_unica.xlsx'.")

if __name__ == "__main__":
    main()
