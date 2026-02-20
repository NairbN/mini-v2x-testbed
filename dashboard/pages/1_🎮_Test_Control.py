#!/usr/bin/env python3
"""
Test Control Center - V2X Dashboard
Configure and launch experiments from the UI
"""

import streamlit as st
import sys
from datetime import datetime
import time

# Add paths to import test_runner
sys.path.append('/app')
from test_runner import get_orchestrator

# Page configuration
st.set_page_config(
    page_title="Test Control Center",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize orchestrator
orchestrator = get_orchestrator()

# Page Title
st.title("🎮 Test Control Center")
st.markdown("Configure and launch V2X performance experiments")

st.divider()

# Section 1: Test Configuration Form
st.subheader("📋 New Experiment Configuration")

with st.form("test_config_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        exp_name = st.text_input(
            "Experiment Name",
            value=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            help="Unique identifier for this test run (alphanumeric and underscores only)",
            placeholder="my_experiment_name"
        )
        duration = st.slider(
            "Duration (seconds)",
            min_value=10,
            max_value=300,
            value=60,
            step=5,
            help="How long to run the experiment"
        )

    with col2:
        network_profile = st.selectbox(
            "Network Profile",
            options=['normal', 'moderate', 'severe', 'handoff'],
            index=1,  # Default to 'moderate'
            help="Simulated network conditions:\n"
                 "- Normal: No degradation (baseline)\n"
                 "- Moderate: 50ms delay, 1% loss\n"
                 "- Severe: 200ms delay, 10% loss\n"
                 "- Handoff: Multi-phase handoff simulation"
        )

        protocol = st.multiselect(
            "Protocols to Test",
            options=['UDP', 'TCP', 'MQTT'],
            default=['UDP', 'TCP', 'MQTT'],
            help="Select which protocols to use (currently tests all selected protocols)"
        )

    # Advanced options (collapsible)
    with st.expander("⚙️ Advanced Options"):
        st.info("Advanced configuration options (coming soon)")

        col_adv1, col_adv2 = st.columns(2)

        with col_adv1:
            custom_delay = st.number_input(
                "Custom delay (ms)",
                min_value=0,
                max_value=500,
                value=0,
                disabled=True,
                help="Custom network delay (requires custom profile - coming soon)"
            )
            custom_loss = st.number_input(
                "Custom loss (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                disabled=True,
                help="Custom packet loss rate (requires custom profile - coming soon)"
            )

        with col_adv2:
            enable_pcap = st.checkbox(
                "Enable packet capture",
                value=True,
                help="Capture network packets for detailed analysis"
            )
            data_points = st.slider(
                "Data points to collect",
                min_value=100,
                max_value=10000,
                value=1000,
                disabled=True,
                help="Maximum messages to display (coming soon)"
            )

    # Form submission
    submitted = st.form_submit_button("🚀 Start Experiment", type="primary", use_container_width=True)

    if submitted:
        # Prepare protocol string
        protocol_str = ','.join(protocol) if protocol else 'ALL'

        # Advanced options dict (for future use)
        advanced_opts = {
            'enable_pcap': enable_pcap,
            'data_points': data_points,
            'custom_delay': custom_delay if custom_delay > 0 else None,
            'custom_loss': custom_loss if custom_loss > 0 else None
        }

        # Start experiment
        result = orchestrator.start_experiment(
            name=exp_name,
            duration=duration,
            profile=network_profile,
            protocol=protocol_str,
            advanced_options=advanced_opts
        )

        # Display result
        if result['success']:
            st.success(f"✅ {result['message']}")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ {result['message']}")

st.divider()

# Section 2: Active Test Monitor
st.subheader("📊 Active Experiment")

# Fetch running experiment
running_exp = orchestrator.get_running_experiment()

if running_exp:
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

    with col1:
        st.metric("Experiment Name", running_exp['experiment_name'])

        # Progress bar
        progress_pct = running_exp.get('progress_percent', 0)
        st.progress(progress_pct / 100, text=f"Progress: {progress_pct}%")

        # Current phase
        phase = running_exp.get('current_phase', 'unknown')
        phase_emoji = {
            'initializing': '🔄',
            'starting_services': '🚀',
            'clearing_data': '🧹',
            'applying_network': '🌐',
            'capturing': '📦',
            'running': '⚡',
            'stopping_capture': '🛑',
            'analyzing': '📊',
            'parsing_pcap': '📈',
            'completed': '✅'
        }
        st.caption(f"{phase_emoji.get(phase, '⚙️')} Phase: **{phase}**")

    with col2:
        st.metric("Duration", f"{running_exp['duration_seconds']}s")

        # Elapsed and remaining time
        if 'elapsed_seconds' in running_exp:
            elapsed = running_exp['elapsed_seconds']
            remaining = running_exp.get('remaining_seconds', 0)
            st.caption(f"⏱️ Elapsed: {elapsed}s")
            st.caption(f"⏳ Remaining: ~{remaining}s")

    with col3:
        st.metric("Network Profile", running_exp['network_profile'])
        protocol_display = running_exp.get('protocol', 'ALL')
        st.caption(f"🔌 Protocol: {protocol_display}")

    with col4:
        st.metric("Status", running_exp['status'].upper())

        # Cancel button
        if st.button("🛑 Cancel Experiment", type="secondary", use_container_width=True):
            cancel_result = orchestrator.cancel_experiment(running_exp['id'])

            if cancel_result['success']:
                st.success(cancel_result['message'])
                time.sleep(1)
                st.rerun()
            else:
                st.error(cancel_result['message'])

    # Auto-refresh while experiment is running
    if running_exp['status'] in ('running', 'pending'):
        time.sleep(2)
        st.rerun()

else:
    st.info("ℹ️ No experiment currently running. Configure and start a new experiment above.")

st.divider()

# Section 3: Recent Experiments
st.subheader("🗂️ Recent Experiments")

# Fetch recent experiments
experiments = orchestrator.list_experiments(limit=15)

if experiments:
    # Status filter
    col_filter1, col_filter2, col_filter3 = st.columns([1, 1, 2])

    with col_filter1:
        status_filter = st.selectbox(
            "Filter by Status",
            options=['All', 'completed', 'running', 'failed', 'cancelled', 'pending'],
            index=0
        )

    # Apply filter
    if status_filter != 'All':
        experiments = [exp for exp in experiments if exp['status'] == status_filter]

    with col_filter2:
        st.caption(f"Showing {len(experiments)} experiment(s)")

    # Display experiments as cards
    for exp in experiments:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])

            # Status emoji
            status_emoji = {
                'running': '🔄',
                'completed': '✅',
                'failed': '❌',
                'pending': '⏳',
                'cancelled': '🚫'
            }

            with col1:
                st.markdown(f"### {status_emoji.get(exp['status'], '❓')} {exp['experiment_name']}")

            with col2:
                st.write(f"**Profile:** {exp['network_profile']}")
                st.caption(f"Duration: {exp['duration_seconds']}s")

            with col3:
                st.write(f"**Status:** {exp['status']}")
                if exp.get('progress_percent'):
                    st.caption(f"Progress: {exp['progress_percent']}%")

            with col4:
                created = exp.get('created_at', 'Unknown')
                if created != 'Unknown':
                    try:
                        created_time = datetime.fromisoformat(created).strftime('%Y-%m-%d %H:%M')
                        st.caption(f"📅 {created_time}")
                    except:
                        st.caption(f"📅 {created}")
                else:
                    st.caption("📅 Unknown")

            with col5:
                # Action buttons
                if exp['status'] == 'completed':
                    if st.button("📈 View Results", key=f"view_{exp['id']}", use_container_width=True):
                        st.session_state['selected_experiment_id'] = exp['id']
                        st.switch_page("pages/2_📈_Results_Viewer.py")

                elif exp['status'] == 'failed':
                    error_msg = exp.get('error_message', 'Unknown error')
                    with st.expander("⚠️ Error Details"):
                        st.error(error_msg)

            st.divider()

else:
    st.info("No experiments found. Start your first experiment above!")

# Footer
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh every 5 seconds if no experiment is running
if not running_exp:
    time.sleep(5)
    st.rerun()
