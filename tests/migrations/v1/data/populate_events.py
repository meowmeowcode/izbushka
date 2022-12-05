from izbushka import Operations


def run(op: Operations) -> None:
    rows = [
        ["user.create"],
        ["user.delete"],
    ]
    op.insert("events", rows, column_names=["operation"])


def get_progress(op: Operations) -> str:
    return "50%"
