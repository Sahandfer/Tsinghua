import matplotlib.pyplot as plt


def plot_loss_and_acc(loss_and_acc_dict):

    max_epoch = len(loss_and_acc_dict)

    loss_list = [t[0] for t in list(loss_and_acc_dict.values())]
    max_loss = max(loss_list)
    min_loss = max(0, min(loss_list))

    fig = plt.figure()

    plt.plot(range(1, 1 + max_epoch), loss_list, "-s")

    plt.title(f"Loss Curve")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.xticks(range(0, max_epoch + 1, 2))
    plt.axis([0, max_epoch, min_loss, max_loss])
    plt.show()

    fig.savefig(f"figures/loss.png", dpi=300)

    acc_list = [t[1] for t in list(loss_and_acc_dict.values())]
    max_acc = max(acc_list)
    min_acc = max(0, min(acc_list))

    fig = plt.figure()

    plt.plot(range(1, 1 + max_epoch), acc_list, "-s")

    plt.title(f"Accuracy Curve")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy (%)")
    plt.xticks(range(0, max_epoch + 1, 2))
    plt.axis([0, max_epoch, min_acc, max_acc])
    plt.show()
    fig.savefig(f"figures/acc.png", dpi=300)