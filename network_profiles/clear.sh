#!/bin/bash
# Clear all network shaping rules

INTERFACE="eth0"

echo "Clearing all tc rules on $INTERFACE..."

tc qdisc del dev $INTERFACE root 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ All network shaping rules cleared"
else
    echo "✓ No rules to clear (already clean)"
fi
