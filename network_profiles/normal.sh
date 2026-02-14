#!/bin/bash
# Normal network conditions (no degradation)

INTERFACE="eth0"

echo "Applying NORMAL network profile..."

# Clear existing tc rules
tc qdisc del dev $INTERFACE root 2>/dev/null

# Add basic qdisc (no degradation)
tc qdisc add dev $INTERFACE root handle 1: prio

echo "✓ Normal network profile applied"
echo "  - No artificial delay"
echo "  - No packet loss"
echo "  - No bandwidth limit"
