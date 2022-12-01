interface=$1
sleep_for_seconds=$2
sleep_until=$(($(date +%s) + sleep_for_seconds))
sleep_until_in_ns=$sleep_until"000000000"

sudo chrt --rr 1 $(poetry run which python) pygoose/publisher_sync.py $interface $sleep_until_in_ns