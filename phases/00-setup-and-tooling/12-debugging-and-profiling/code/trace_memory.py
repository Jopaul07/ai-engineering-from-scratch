import tracemalloc


def read_raw():
    return [bytearray(1024) for _ in range(200)]


def preprocess(raw):
    return [bytes(row) for row in raw]


def load_data():
    raw = read_raw()
    processed = preprocess(raw)
    return processed


def main():
    # Snapshot 1: before any allocation
    tracemalloc.start()
    snap1 = tracemalloc.take_snapshot()

    # Snapshot 2: after read_raw() only — its bytearrays are still alive via `raw`
    raw = read_raw()
    snap2 = tracemalloc.take_snapshot()

    # Snapshot 3: after preprocess() copies raw into new bytes objects
    processed = preprocess(raw)
    snap3 = tracemalloc.take_snapshot()

    # Free raw — its 200 bytearrays become garbage, collected before snap4
    del raw
    snap4 = tracemalloc.take_snapshot()

    def top(snapshot, label):
        print(f"\nTop 5 lines for {label}:")
        for stat in snapshot.statistics("lineno")[:5]:
            print(f"  {stat}")

    top(snap1, "snap1 (nothing allocated)")
    top(snap2, "snap2 (after read_raw)")
    top(snap3, "snap3 (after preprocess)")
    top(snap4, "snap4 (after del raw)")

    # Diff: what grew between snap3 and snap4? Freed memory shows as negative.
    print("\nDiff snap4 vs snap3 (what changed after del raw):")
    for stat in snap4.compare_to(snap3, "lineno")[:5]:
        print(f"  {stat}")

    tracemalloc.stop()
    return len(processed)


if __name__ == "__main__":
    main()
