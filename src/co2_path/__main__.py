"""Print the evidence record as JSON."""

import json

from .mechanism import neutral_atomic_carbon_channel


def main() -> None:
    print(json.dumps(neutral_atomic_carbon_channel().as_dict(), indent=2))


if __name__ == "__main__":
    main()
