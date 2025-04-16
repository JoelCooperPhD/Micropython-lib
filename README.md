```markdown
# Micropython-lib by Joel Cooper

This repository contains standalone MicroPython libraries for embedded development. Each library is installable on MicroPython devices using `mpremote` and the `mip` installer.

## Installation

Install any library with:

```bash
mpremote connect mip install github:JoelCooperPhD/Micropython-lib/<package_name>
```

Example:

```bash
mpremote connect auto mip install github:JoelCooperPhD/Micropython-lib/debounce
```

## Available Libraries

### `debounce`

Asynchronous and interrupt-based GPIO debounce utilities.

- `AsyncPinMonitor`: polling-based debounce using `uasyncio`
- `EdgeTimedIRQ`: interrupt-based debounce using edge timing

[Usage and examples](./debounce/README.md)

## Requirements

- MicroPython v1.19 or later
- `mpremote` installed:

```bash
pip install mpremote
```

## License

MIT License © Joel Cooper
```
