import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

def count(df):

    pr_odchylenia = 2
    proby = 200
    start_val = df["Zamkniecie"].iloc[0]
    odchylenie = 5
    set = pd.DataFrame({'Zamkniecie': [start_val] * len(df["Zamkniecie"])})

    plt.figure(figsize=(15,10), dpi=100)
    for i in range(proby):
        data = [start_val]
        for k in range(1,len(set)):
            next = data[-1] * (1 + random.randint(-pr_odchylenia, pr_odchylenia) / 100)
            data.append(next)

        final_val = data[-1]  # Wartość końcowa symulacji

        # LOGIKA KOLOROWANIA:
        # Sprawdzamy, czy końcowa wartość mieści się w przedziale [start-5, start+5]
        if (df["Zamkniecie"].iloc[-1] - odchylenie) <= final_val <= (df["Zamkniecie"].iloc[-1] + odchylenie):
            alpha = 0.55  # Bardziej widoczne
            linewidth = 2
        else:
            alpha = 0.4
            linewidth = 1

        name = f"w{i}"
        set[name] = data
        color = (random.random(), random.random(), random.random())
        plt.plot(df["Data"], set[name], linewidth=linewidth, color=color, alpha=alpha)

    plt.plot(df["Data"], df["Zamkniecie"], label="Zamkniecie", color="black")
    # plt.axhline(y=df["Zamkniecie"] + odchylenie, color='black', linestyle='--', alpha=0.3, label='Granica +5')
    # plt.axhline(y=df["Zamkniecie"] - odchylenie, color='black', linestyle='--', alpha=0.4, label='Granica -5')

    plt.xticks(rotation=45, fontsize=5 )
    plt.title(f"Symulacja Monte Carlo: {proby} scenariuszy", fontsize=16)
    plt.xlabel("Dzień", fontsize=12)
    plt.ylabel("Wartość", fontsize=12)
    plt.show()