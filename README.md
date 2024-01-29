# PyGOOSE

IEC 61850 GOOSE publisher/subscriber in Python.

## Ubuntu Quickstart

pygoose should be ran as sudo.

### Pre-Requirements

```bash
sudo apt update
sudo apt install -y python3-venv
```

### Installing

```bash
git clone https://github.com/arthurazs/pygoose
cd pygoose
python3 -m venv .venv
. .venv/bin/activate
pip install .[async]
```

### Running

Remember to change `lo` to your interface name. Use the `ip -br a` command to see your interfaces.

```bash
sudo .venv/bin/python pygoose/publisher_async.py lo 0
# sudo .venv/bin/python -m pygoose -ap  # publish goose 
```

## Roadmap

- [x] TimeQuality
- [ ] TimeStamp
  - [x] FractionOfSecond