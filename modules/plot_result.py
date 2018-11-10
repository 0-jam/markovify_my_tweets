import matplotlib.pyplot as plt
import tkinter as tki

def plot_result(losses):
    fig = plt.figure()
    ax = fig.subplots()

    ax.set(xlabel="epoch", ylabel="loss", xticks=range(len(losses)))
    ax.plot(losses)

    return fig

def save_result(losses, save_to="result.png"):
    plot_result(losses).savefig(save_to)

def show_result(losses):
    plot_result(losses).show()
    tki.mainloop()
