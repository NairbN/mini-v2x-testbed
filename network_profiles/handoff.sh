#!/bin/bash
# Handoff scenario (simulates cell tower handoff with temporary disruption)

INTERFACE="eth0"

echo "Simulating HANDOFF scenario..."

# Clear existing tc rules
tc qdisc del dev $INTERFACE root 2>/dev/null

# Phase 1: Pre-handoff (normal with slight degradation)
echo "Phase 1: Pre-handoff (2s)"
tc qdisc add dev $INTERFACE root handle 1: htb default 12
tc class add dev $INTERFACE parent 1: classid 1:12 htb rate 20mbit
tc qdisc add dev $INTERFACE parent 1:12 handle 10: netem delay 30ms loss 0.5%

sleep 2

# Phase 2: During handoff (severe disruption)
echo "Phase 2: Handoff disruption (3s)"
tc qdisc change dev $INTERFACE parent 1:12 handle 10: netem \
    delay 300ms 100ms \
    loss 30% \
    limit 1000

sleep 3

# Phase 3: Post-handoff recovery
echo "Phase 3: Recovery (2s)"
tc qdisc change dev $INTERFACE parent 1:12 handle 10: netem \
    delay 50ms 20ms \
    loss 2%

sleep 2

# Phase 4: Return to normal
echo "Phase 4: Stabilized"
tc qdisc change dev $INTERFACE parent 1:12 handle 10: netem delay 25ms loss 0.5%

echo "✓ Handoff scenario complete"
