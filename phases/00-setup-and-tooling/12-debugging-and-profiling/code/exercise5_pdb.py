"""Exercise 5: breakpoint() drill — inspect shapes, devices, gradients in pdb.

Run with: .venv/bin/python -m pdb exercise5_pdb.py
Or pipe commands: .venv/bin/python - <<'CMDS' ... (see exercise5_pdb.py bottom)
"""

import torch
import torch.nn as nn


def train_step(model, batch, criterion, optimizer, step):
    inputs, labels = batch
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    loss.backward()

    # The drill: stop right after backward(), when gradients are live.
    breakpoint()  # drop into pdb here

    optimizer.step()
    return loss


def main():
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(8, 32), nn.ReLU(), nn.Linear(32, 2))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    x = torch.randn(16, 8)
    y = torch.randint(0, 2, (16,))

    for step in range(2):
        loss = train_step(model, (x, y), criterion, optimizer, step)
        print(f"step {step}: loss={loss.item():.4f}")


if __name__ == "__main__":
    main()
