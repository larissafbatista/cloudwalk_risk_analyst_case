# Importing libs
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Reading data
df = pd.read_csv('transactional-sample.txt', sep=',', header=0)

# Pre-processing | Encoding datetime
def encoding_datetime():
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    df['date_year'] = df['transaction_date'].dt.year
    df['date_month'] = df['transaction_date'].dt.month
    df['date_day'] = df['transaction_date'].dt.day
    df['date_dow'] = df['transaction_date'].dt.dayofweek
    df['hour'] = df['transaction_date'].dt.hour
    df['min'] = df['transaction_date'].dt.minute
    df['sec'] = df['transaction_date'].dt.second
    # print(df.head())

# Pre-processing | Encoding card number
def encoding_card_number():
    df['card_number_end'] = [i[13:] for i in df['card_number']]


encoding_datetime()
encoding_card_number()


# 1. Risk Index I | Reject transaction if user is trying too many transactions in a row;
def detecting_repetitions():
    df_id = pd.DataFrame(df, columns=['merchant_id', 'user_id', 'card_number_end']) #
    df_id['match_merch_id'] = df.merchant_id.eq(df.merchant_id.shift())
    df_id['match_user_id'] = df.user_id.eq(df.user_id.shift())
    df_id['match_card_id'] = df.card_number_end.eq(df.card_number_end.shift())

    df['index_i'] = df_id.all(axis='columns') # Checking if values are equal
    df['index_i'].replace({False: 0, True: 1}, inplace=True)


print(f'index_i \n {df.head(15)}')



# 2. Risk Index II | Reject transaction if a user had a chargeback before
def detecting_previous_cbk():
    df['dupli'] = df['user_id'].duplicated() # Finding duplicates
    df_prev = pd.DataFrame(df, columns=['dupli', 'has_cbk'])
    df['index_ii'] = df_prev.all(axis='columns') # Checking if both values are equal
    df['index_ii'].replace({False: 0, True: 1}, inplace=True)


print(f'index_ii \n {df.head(15)}')


# 3. Risk Index III | Reject transactions above a certain amount in a given period
def detecting_outliers():

    sns.boxplot(df['transaction_amount']) # Box plot
    plt.show()

    df['index_iii'] = np.where(df.transaction_amount > 2200, 1, 0)


detecting_repetitions()
detecting_previous_cbk()
detecting_outliers()
print(df.head(15))


# 4. Combining indexes
df_combined = pd.DataFrame(df, columns=['transaction_id', 'index_i', 'index_ii', 'index_iii'])
df_combined['recommendation'] = df_combined.iloc[:, 1:].sum(axis=1) # Summing the index values
df_combined['recommendation'].replace({0: 'approve', 1: 'approve', 2: 'deny', 3: 'deny'}, inplace=True)
print(df_combined)