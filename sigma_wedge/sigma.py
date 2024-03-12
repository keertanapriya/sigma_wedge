import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv("data.csv")

closing_price_columns = [col for col in data.columns if col != 'Date' and col != 'Field']
portfolio_values = {}
optimal_buy_indices = {}

#Transition states are -1(bear),1(bull),0(flat)
transition_counts = {'00': 0, '01': 0, '0-1': 0, '10': 0, '11': 0, '1-1': 0, '-10': 0, '-11': 0, '-1-1': 0}
fig, axes = plt.subplots(len(closing_price_columns), 1, figsize=(10, 5 * len(closing_price_columns)), sharex=True)

for col, ax in zip(closing_price_columns, axes):
    data[col + '_Returns'] = data[col].pct_change()
    
    def classify_state(return_val):
        if return_val >= 0.01:
            return 1
        elif return_val > -0.01:
            return 0
        else:
            return -1
    
    # Apply state classification
    data[col + '_State'] = data[col + '_Returns'].apply(classify_state)

    # Calculate portfolio value and identify optimal buy indices
    portfolio_value = 0
    buy_indices = set()
    for i in range(1, len(data)):
        if data.loc[i, col + '_State'] == 1 and data.loc[i - 1, col + '_State'] == 0:
            buy_indices.add(i)
            portfolio_value += 1
            transition_counts['01'] += 1
        elif data.loc[i, col + '_State'] == -1 and data.loc[i - 1, col + '_State'] == 0:
            buy_indices.add(i)
            portfolio_value -= 1
            transition_counts['-1-1'] += 1
        elif data.loc[i - 1, col + '_State'] == 0:
            if data.loc[i, col + '_State'] == 0:
                transition_counts['00'] += 1
            elif data.loc[i, col + '_State'] == 1:
                transition_counts['01'] += 1
            else:
                transition_counts['0-1'] += 1
        elif data.loc[i - 1, col + '_State'] == 1:
            if data.loc[i, col + '_State'] == 0:
                transition_counts['10'] += 1
            elif data.loc[i, col + '_State'] == 1:
                transition_counts['11'] += 1
            else:
                transition_counts['1-1'] += 1
        else:
            if data.loc[i, col + '_State'] == 0:
                transition_counts['-10'] += 1
            elif data.loc[i, col + '_State'] == 1:
                transition_counts['-11'] += 1
            else:
                transition_counts['-1-1'] += 1
    
    portfolio_values[col] = portfolio_value
    optimal_buy_indices[col] = buy_indices

    # Plot closing prices for each SID
    closing_prices = data[col].values
    dates = data['Date'].values
    ax.plot(dates, closing_prices, label='Closing Prices', color='blue')
    
    for index in buy_indices:
        ax.axvline(x=index, color='pink', linestyle='--', alpha=0.5)
    
    ax.set_title(f"SID: {col}")
    ax.set_ylabel("Closing Price")
    ax.legend()

axes[-1].set_xlabel("Date")
plt.tight_layout()
plt.show()

sum_1 = 0
print("Portfolio Values:")
for col, value in portfolio_values.items():
    print(f"Portfolio value for {col}: {value}")
    sum_1 = sum_1 + value
print(f"\nTotal portfolio value: {sum_1}\n")
print("---------------------------------------------------")
print("\nOptimal Buy Indices:")
for col, indices in optimal_buy_indices.items():
    print(f"Optimal buy indices for {col}:\n {list(indices)}\n")
print("---------------------------------------------------")
print("\nTransition Probabilities:")
total_transitions = sum(transition_counts.values())
for transition, count in transition_counts.items():
    probability = count / total_transitions
    print(f"{transition}: {probability}")
