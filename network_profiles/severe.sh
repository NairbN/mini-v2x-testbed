#!/bin/bash
# Severe network degradation (congested network or poor coverage)

INTERFACE="eth0"

echo "Applying SEVERE degradation profile..."

# Clear existing tc rules
tc qdisc del dev $INTERFACE root 2>/dev/null

# Add root qdisc
tc qdisc add dev $INTERFACE root handle 1: htb default 12

# Add class with strict bandwidth limit
tc class add dev $INTERFACE parent 1: classid 1:12 htb rate 2mbit ceil 5mbit

# Add netem for significant delay, jitter, and loss
tc qdisc add dev $INTERFACE parent 1:12 handle 10: netem \
    delay 200ms 50ms distribution normal \
    loss 10% 25% \
    limit 1000 \
    reorder 5% 25%

echo "✓ Severe degradation profile applied"
echo "  - Delay: 200ms ± 50ms"
echo "  - Packet loss: 10% (25% correlation)"
echo "  - Bandwidth: 2-5 Mbit/s"
echo "  - Reordering: 5%"
