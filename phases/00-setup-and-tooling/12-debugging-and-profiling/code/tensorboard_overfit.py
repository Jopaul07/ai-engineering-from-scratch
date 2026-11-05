"""Exercise 4: TensorBoard run — train a deliberately overfitting model.

Logs train/val loss per epoch plus weight and gradient histograms to
runs/overfit_demo, then prints the epoch where val loss started rising.
"""

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter


def main():
    torch.manual_seed(0)

    # Tiny train set (32 samples, 8 features, lots of noise) so the model
    # memorizes it; a separate noisy val set it has never seen.
    x_train = torch.randn(32, 8)
    y_train = (x_train.sum(dim=1) > 0).float() + 0.05 * torch.randn(32)
    x_val = torch.randn(32, 8)
    y_val = (x_val.sum(dim=1) > 0).float() + 0.05 * torch.randn(32)

    model = nn.Sequential(
        nn.Linear(8, 64), nn.ReLU(),
        nn.Linear(64, 64), nn.ReLU(),
        nn.Linear(64, 1),
    )
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    writer = SummaryWriter("runs/overfit_demo")

    val_rise_epoch = None
    best_val = float("inf")

    for epoch in range(300):
        # ---- train step (full-batch, tiny data) ----
        model.train()
        optimizer.zero_grad()
        train_loss = criterion(model(x_train).squeeze(), y_train)
        train_loss.backward()
        optimizer.step()

        # ---- validation ----
        model.eval()
        with torch.no_grad():
            val_loss = criterion(model(x_val).squeeze(), y_val)

        writer.add_scalar("loss/train", train_loss.item(), epoch)
        writer.add_scalar("loss/val", val_loss.item(), epoch)
        writer.add_scalar("lr", optimizer.param_groups[0]["lr"], epoch)

        if epoch % 20 == 0:
            for name, param in model.named_parameters():
                writer.add_histogram(f"weights/{name}", param, epoch)
                if param.grad is not None:
                    writer.add_histogram(f"grads/{name}", param.grad, epoch)

        # detect the overfitting point: val loss starts rising after a best
        if val_loss.item() < best_val - 1e-4:
            best_val = val_loss.item()
            val_rise_epoch = None
        elif val_rise_epoch is None and epoch > 10:
            val_rise_epoch = epoch

    writer.close()

    print(f"Final train loss: {train_loss.item():.4f}")
    print(f"Final val loss:   {val_loss.item():.4f}")
    print(f"Best val loss:    {best_val:.4f}")
    print(f"Val loss rising since epoch: {val_rise_epoch}")
    verdict = (
        "OVERFITTING"
        if (val_loss.item() > best_val * 1.1 and train_loss.item() < val_loss.item() * 0.5)
        else "not overfitting"
    )
    print(f"Verdict: model is {verdict}")


if __name__ == "__main__":
    main()
