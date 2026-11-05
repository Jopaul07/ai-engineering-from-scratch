import time

import torch
import torch.nn as nn


def slow_data_augment(batch):
    """Deliberately slow: simulates per-sample I/O-bound augmentation."""
    time.sleep(0.01)
    out = []
    for row in batch:
        out.append(row * 1.000001)
    return torch.stack(out)


def fast_data_augment(batch):
    return batch * 1.000001


def train_loop(model, x, target, criterion, optimizer, steps=20):
    for step in range(steps):
        batch = slow_data_augment(x)
        optimizer.zero_grad()
        output = model(batch)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()


def main():
    model = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 10))
    x = torch.randn(128, 784)
    target = torch.randint(0, 10, (128,))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    train_loop(model, x, target, criterion, optimizer, steps=20)


if __name__ == "__main__":
    main()
