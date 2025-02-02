import streamlit as st
import random

st.title("Supply Chain Integration Game - 6 Players 🏭")

# Initialize game state
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'players': {
            f'Player {i+1}': {
                'money': 500,
                'facilities': {
                    "Supplier 📦": {'owned': False, 'rented': False},
                    "Warehouse 🏪": {'owned': False, 'rented': False},
                    "Factory 🏭": {'owned': False, 'rented': False},
                    "Distribution Center 🚛": {'owned': False, 'rented': False},
                    "Retail Store 🛍️": {'owned': False, 'rented': False}
                }
            } for i in range(6)
        },
        'monthly_income': 100,
        'months': 0,
        'current_player_index': 0
    }
    st.session_state.prices = {facility: random.randint(200, 400) for facility in st.session_state.game_state['players']['Player 1']['facilities']}
    st.session_state.rental_prices = {facility: price // 4 for facility, price in st.session_state.prices.items()}

# Get current player
current_player = f"Player {st.session_state.game_state['current_player_index'] + 1}"

# Display game status for all players
st.write("### Players Status:")
for player, data in st.session_state.game_state['players'].items():
    st.write(f"{player}'s Balance: ${data['money']} 💰")

st.write(f"### Month: {st.session_state.game_state['months']} 📅")
st.write(f"### Current Turn: {current_player}")

# Display facilities and actions for current player
st.write(f"### {current_player}'s Supply Chain:")
for facility, status in st.session_state.game_state['players'][current_player]['facilities'].items():
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        status_text = "✅ Owned" if status['owned'] else "🔄 Rented" if status['rented'] else "❌ Not acquired"
        st.write(f"{facility}: {status_text}")

    if not status['owned']:
        with col2:
            if not status['rented']:
                if st.button(f"Rent ${st.session_state.rental_prices[facility]}/month", key=f"rent_{facility}"):
                    if st.session_state.game_state['players'][current_player]['money'] >= st.session_state.rental_prices[facility]:
                        st.session_state.game_state['players'][current_player]['money'] -= st.session_state.rental_prices[facility]
                        st.session_state.game_state['players'][current_player]['facilities'][facility]['rented'] = True
                        st.success(f"Successfully rented {facility}!")
                        st.rerun()
                    else:
                        st.error("Not enough money!")
            else:
                if st.button(f"Buy (Upgrade) ${st.session_state.prices[facility]}", key=f"buy_upgrade_{facility}"):
                    if st.session_state.game_state['players'][current_player]['money'] >= st.session_state.prices[facility]:
                        st.session_state.game_state['players'][current_player]['money'] -= st.session_state.prices[facility]
                        st.session_state.game_state['players'][current_player]['facilities'][facility]['owned'] = True
                        st.session_state.game_state['players'][current_player]['facilities'][facility]['rented'] = False
                        st.success(f"Successfully purchased {facility}!")
                        st.rerun()
                    else:
                        st.error("Not enough money!")

        with col3:
            if not status['rented']:
                if st.button(f"Buy ${st.session_state.prices[facility]}", key=f"buy_{facility}"):
                    if st.session_state.game_state['players'][current_player]['money'] >= st.session_state.prices[facility]:
                        st.session_state.game_state['players'][current_player]['money'] -= st.session_state.prices[facility]
                        st.session_state.game_state['players'][current_player]['facilities'][facility]['owned'] = True
                        st.success(f"Successfully purchased {facility}!")
                        st.rerun()
                    else:
                        st.error("Not enough money!")

        with col4:
            if status['owned']:
                if st.button(f"Sell ${st.session_state.prices[facility]}", key=f"sell_{facility}"):
                    st.session_state.game_state['players'][current_player]['money'] += st.session_state.prices[facility] // 2
                    st.session_state.game_state['players'][current_player]['facilities'][facility]['owned'] = False
                    st.success(f"Successfully sold {facility}!")
                    st.rerun()
            elif status['rented']:
                if st.button(f"Stop Renting", key=f"stop_renting_{facility}"):
                    st.session_state.game_state['players'][current_player]['facilities'][facility]['rented'] = False
                    st.rerun()

# End Turn button
if st.button("End Turn ⏭️"):
    # Calculate income and costs for current player
    owned_facilities = sum(1 for f in st.session_state.game_state['players'][current_player]['facilities'].values() if f['owned'])
    rented_facilities = sum(1 for f in st.session_state.game_state['players'][current_player]['facilities'].values() if f['rented'])

    owned_income = owned_facilities * st.session_state.game_state['monthly_income']
    rental_income = rented_facilities * (st.session_state.game_state['monthly_income'] // 2)
    total_income = owned_income + rental_income
    rental_costs = sum(st.session_state.rental_prices[f] for f, status in st.session_state.game_state['players'][current_player]['facilities'].items() if status['rented'])

    st.session_state.game_state['players'][current_player]['money'] += total_income - rental_costs

    # Move to next player
    st.session_state.game_state['current_player_index'] = (st.session_state.game_state['current_player_index'] + 1) % 6
    
    # If we've completed a round, increment the month
    if st.session_state.game_state['current_player_index'] == 0:
        st.session_state.game_state['months'] += 1
    
    st.info(f"""
    Turn Summary for {current_player}:
    Income from owned facilities: ${owned_income}
    Income from rented facilities: ${rental_income}
    Rental costs: -${rental_costs}
    Net income: ${total_income - rental_costs}
    """)
    st.rerun()

# Check for winners
winners = []
for player, data in st.session_state.game_state['players'].items():
    if all(status['owned'] for status in data['facilities'].values()):
        winners.append(player)

if winners:
    st.balloons()
    st.success(f"🎉 Congratulations! {', '.join(winners)} have built complete supply chains!")
    if st.button("Play Again 🔄"):
        del st.session_state.game_state
        st.rerun()

# Check for eliminated players
eliminated = []
for player, data in st.session_state.game_state['players'].items():
    if data['money'] < 0:
        eliminated.append(player)

if eliminated:
    st.error(f"💔 {', '.join(eliminated)} have been eliminated due to bankruptcy!")
    if len(eliminated) == 6:  # All players eliminated
        if st.button("Start New Game 🔄"):
            del st.session_state.game_state
            st.rerun()
