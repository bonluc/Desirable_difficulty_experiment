import pandas as pd

def generate_rounds_data(results_df, round_df, round_number, rounds):
    condition = round_df["condition"].iloc[0]  # same for all rows in the round
    # Total time spent in the round
    total_time = round_df["time_spent"].sum()
    recalled_words = []
    for word in results_df[f'round{round_number}']:
        if type(word) == str:
            recalled_words.append(word)
    rounds['round'].append(round_number)
    rounds['condition'].append(condition)
    rounds['total_time'].append(round(total_time, 2))
    rounds['total_words'].append(len(recalled_words))
    #print(rounds)
    return rounds

if __name__ == '__main__':
    participants_data = {'participant': [], 'avg_words_normal':[], 'avg_words_mirrored':[], 'avg_normal_time(s)': [], 'avg_mirrored_time(s)': []} 
    for participant in range(1,7):
        rounds = {'round': [], 'condition': [], 'total_time': [], 'total_words': []}
        #results_df = pd.read_excel(f"participants_results\participant_{participant}\participant_{participant}_results.xlsx")
        results_df = pd.read_excel(f"participants_results/participant_{participant}/participant_{participant}_results.xlsx")

        for round_number in range(1,7):
            round_df = pd.read_csv(f"participants_results/participant_{participant}/round_{round_number}.csv")

            rounds = generate_rounds_data(results_df, round_df, round_number, rounds)
        rounds_df = pd.DataFrame(rounds)
        participants_data['participant'].append(participant)
        avg_normal = rounds_df[rounds_df['condition']=='normal']['total_words'].mean()
        avg_mirrored = rounds_df[rounds_df['condition']=='mirrored']['total_words'].mean()
        avg_normal_time = rounds_df[rounds_df['condition']=='normal']['total_time'].mean()
        avg_mirrored_time = rounds_df[rounds_df['condition']=='mirrored']['total_time'].mean()
        participants_data['avg_words_normal'].append(round(avg_normal,2))
        participants_data['avg_words_mirrored'].append(round(avg_mirrored,2))
        participants_data['avg_normal_time(s)'].append(round(avg_normal_time, 2))
        participants_data['avg_mirrored_time(s)'].append(round(avg_mirrored_time, 2))
        # save rounds data in the participant folder
        rounds_df.to_csv(fr'participants_results/participant_{participant}/participant_{participant}_rounds_summary.csv', index=False)

    participants_df = pd.DataFrame(participants_data)
    participants_df.to_csv('participants_summary.csv', index=False)
    participants_summary = pd.read_csv('participants_summary.csv')
    print(participants_summary)

        