import os
import time
import pandas as pd
from main import Instance, tabu_search  # importe também tabu_search se for usar


# Caminho das instâncias
INSTANCIA_DIR = r"C:\Users\leonardo.gaertner\Desktop\Tabu\Instancias"
INSTANCIA_PREFIX = "instance_"
INSTANCIA_SUFFIX = ".txt"
NUM_INSTANCIAS = 10
TIME_LIMIT = 300  # segundos (5 minutos por instância)

# Parâmetros iniciais
TABU_TENURE_INIT = [5, 10, 15]
MAX_ITERATIONS_INIT = [50, 100, 200]
NEIGHBORHOOD_SIZE_INIT = [10, 20, 30]

# Valor de incremento e limite de tentativas sem melhoria
INCREMENT = 10
MAX_NO_IMPROVE = 3

# Lista para salvar os resultados
resultados = []

def load_instancias():
    instancias = []
    for i in range(1, NUM_INSTANCIAS + 1):
        nome = f"{INSTANCIA_PREFIX}{str(i).zfill(4)}{INSTANCIA_SUFFIX}"
        caminho = os.path.join(INSTANCIA_DIR, nome)
        instancias.append((nome, Instance.read_instance(caminho)))
    return instancias

def avaliar_parametro(nome_param, valores, fixos, instancias):
    historico_objetivos = []
    sem_melhora = 0
    melhor_media = -float('inf')

    while sem_melhora < MAX_NO_IMPROVE:
        nova_execucao = valores[-1] + INCREMENT if valores else INCREMENT
        valores.append(nova_execucao)
        objetivos = []

        print(f"\nTestando {nome_param} = {nova_execucao}...")

        for nome_inst, inst in instancias:
            # Define os valores atuais dos parâmetros
            config = {
                "TABU_TENURE": nova_execucao if nome_param == "TABU_TENURE" else fixos["TABU_TENURE"],
                "MAX_ITERATIONS": nova_execucao if nome_param == "MAX_ITERATIONS" else fixos["MAX_ITERATIONS"],
                "NEIGHBORHOOD_SIZE": nova_execucao if nome_param == "NEIGHBORHOOD_SIZE" else fixos["NEIGHBORHOOD_SIZE"]
            }

            inicio = time.time()
            sol = tabu_search(inst,
                              time_limit=TIME_LIMIT,
                              tabu_tenure=config["TABU_TENURE"],
                              max_iterations=config["MAX_ITERATIONS"],
                              neighborhood_size=config["NEIGHBORHOOD_SIZE"])
            fim = time.time()

            if sol.orders:
                objetivos.append(sol.objective)
                resultados.append({
                    "Instância": nome_inst,
                    "Parâmetro ajustado": nome_param,
                    "Valor": nova_execucao,
                    "TABU_TENURE": config["TABU_TENURE"],
                    "MAX_ITERATIONS": config["MAX_ITERATIONS"],
                    "NEIGHBORHOOD_SIZE": config["NEIGHBORHOOD_SIZE"],
                    "Objetivo": sol.objective,
                    "Tempo (s)": round(fim - inicio, 2),
                    "Nº Pedidos": len(sol.orders),
                    "Nº Corredores": len(sol.aisles)
                })

        if objetivos:
            media = sum(objetivos) / len(objetivos)
            print(f"→ Média da função objetivo: {media:.2f}")
            historico_objetivos.append(media)

            if media > melhor_media:
                melhor_media = media
                sem_melhora = 0
            else:
                sem_melhora += 1
        else:
            print("→ Nenhuma solução viável encontrada. Ignorando valor.")
            sem_melhora += 1

    return valores, historico_objetivos

def main():
    print("Carregando instâncias...")
    instancias = load_instancias()
    print("Instâncias carregadas.")

    # Valores médios fixos iniciais para parâmetros não ajustados
    fixos = {
        "TABU_TENURE": 10,
        "MAX_ITERATIONS": 100,
        "NEIGHBORHOOD_SIZE": 20
    }

    # Ajusta cada parâmetro individualmente
    print("\nAjustando TABU_TENURE...")
    tenure_vals, _ = avaliar_parametro("TABU_TENURE", TABU_TENURE_INIT.copy(), fixos, instancias)

    fixos["TABU_TENURE"] = max(tenure_vals)

    print("\nAjustando MAX_ITERATIONS...")
    it_vals, _ = avaliar_parametro("MAX_ITERATIONS", MAX_ITERATIONS_INIT.copy(), fixos, instancias)

    fixos["MAX_ITERATIONS"] = max(it_vals)

    print("\nAjustando NEIGHBORHOOD_SIZE...")
    neigh_vals, _ = avaliar_parametro("NEIGHBORHOOD_SIZE", NEIGHBORHOOD_SIZE_INIT.copy(), fixos, instancias)

    fixos["NEIGHBORHOOD_SIZE"] = max(neigh_vals)

    print("\nMelhor configuração encontrada:")
    print(f"TABU_TENURE = {fixos['TABU_TENURE']}")
    print(f"MAX_ITERATIONS = {fixos['MAX_ITERATIONS']}")
    print(f"NEIGHBORHOOD_SIZE = {fixos['NEIGHBORHOOD_SIZE']}")

    df = pd.DataFrame(resultados)
    df.to_excel("ajuste_parametros_resultado.xlsx", index=False)
    print("\nResultados salvos em 'ajuste_parametros_resultado.xlsx'.")

if __name__ == "__main__":
    main()
