#!/bin/bash
# Moderate network degradation (typical urban LTE congestion)

INTERFACE="eth0"

echo "Applying MODERATE degradation profile..."

# Clear existing tc rules
tc qdisc del dev $INTERFACE root 2>/dev/null

# Add root qdisc
tc qdisc add dev $INTERFACE root handle 1: htb default 12

# Add class with bandwidth limit
tc class add dev $INTERFACE parent 1: classid 1:12 htb rate 10mbit ceil 15mbit

# Add netem for delay, jitter, and loss
tc qdisc add dev $INTERFACE parent 1:12 handle 10: netem \
    delay 50ms 10ms distribution normal \
    loss 1% \
    limit 1000

echo "✓ Moderate degradation profile applied"
echo "  - Delay: 50ms ± 10ms"
echo "  - Packet loss: 1%"
echo "  - Bandwidth: 10-15 Mbit/s"
