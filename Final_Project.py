# Initialize imported modules
import seaborn as sns
import pandas as pd
import random
import matplotlib.pyplot as plt
from fpdf import FPDF
fpdf = FPDF()

# Create input variables
principal = int(input('Please enter starting amount: '))
monthly_save = int(input('Please enter your monthly savings goal: '))
monthly_spend = int(input('Please enter your monthly retirement spending goal: '))
years_save = int(input('Please enter number of years to save for: '))
years_spend = int(input('Please enter number of planned full retirement years: '))

# Read and sythesize basic data
figure_size = 120                               # size of figure in mm
a4_size = [210, 297]                            # W x H of a4 paper, MM
data = pd.read_csv('data_csv.csv')
data = list(zip(data['Date'], data['SP500']))
SP500 = []

for i in range(len(data)-1):                    # This creates a list that contains all the % differeneces between all days, giving us a list of decimal values.
    x = data[i+1][1] - data[i][1]
    x = x / data[i][1]
    SP500.append(round(x, 4))

# Define functions for better readability
def dataset_seeds(sample_size):                 # Gives a sample size of a random indexes from SP500 to use (list form)
    return random.sample(range(len(SP500)-((years_save+years_spend)*12)), sample_size)

def interest(principal, rate):                  # Calc interest
    return principal * (1 + rate)

def calc(plant):                                #Calculate every possible x year length instance in our seed list to create a list of values
    dataset = []
    for seed in plant:
        y = principal
        for num in range((years_save+years_spend)*12):
            y = round(interest(y, SP500[seed + num]), 2)
            dataset.append([data[seed][0], num, (y/1000000)])
            if num < years_save*12:
                y += monthly_save
            else:
                y -= monthly_spend
    return dataset
            
def success_chance(dataset):                    #Determine sucess rate of a given set of inputs
    success = 0
    total = 0
    for list in dataset[((years_save+years_spend)*12)-1::(years_save+years_spend)*12]:
        total += 1
        if list[2] > 0:
            success += 1
    return round((success/total)*100, 2)

def creategraph(num, graph_type = True, TF = False, sample_size = (len(SP500)-((years_save+years_spend)*12))):         # Brings everything together to create graphs
    dataset = calc(dataset_seeds(sample_size))
    dataframe = pd.DataFrame(dataset, columns = ['Date', 'Month', 'Value'])                                            # Create a DataFrame with useable data to create a graph from
    if graph_type:
        graph = sns.lineplot(x='Month', y='Value', data=dataframe, errorbar=('pi', 100), linewidth=1)
    else:
        graph = sns.lineplot(x='Month', y='Value', data=dataframe, hue='Date', linewidth=1)
        plt.legend(loc='upper left', title = 'Start Date')
        graph.get_legend().set_visible(TF)
    graph.axhline(y=0, linewidth=2, color='#FF0000')
    graph.axvline(x=(years_save*12), linewidth=2, color='#33FF33')
    graph.set_title(f'Plot{num}')
    plt.ylabel('Value, in Millions')
    plt.xlabel('Months')
    plt.gcf().set_dpi(2000)
    plt.savefig(f'plot{num}.png')
    plt.clf()
    return success_chance(dataset)

# Create Graphs
test1 = creategraph(1)                          # Graph 1, human readable        
test2 = creategraph(2, False, True, 8)          # Graph 2, human readable
test3 = creategraph(3, False)                   # Graph 3, not human readable

# Create texts
text1 = f'The FIREcalc is a data-driven retirement calculator based on 147 years of \
historical S&P 500 stock index data. This tool uses modules such as SEABORN \
and FPDF to help vizualize the data. This is not investment advice, and \
should not be treated as such.'
text2 = f'You started with ${principal} and saved ${monthly_save} a month for {years_save} years. \
You lived for {years_spend} years while spending ${monthly_spend} a month. Your chosen \
lifestyle historically has had a {test1}% success rate. The above graph shows the min, \
max, and an average line of every possible {years_save + years_spend} year segment from \
1871 to 2018 on a monthly basis. Below is a more readable selection of 8 possible futures \
and the dates when the investments started. The red line indicates the $0 line, and the \
green marks the start of retirement.'

# .pdf manipulation section
fpdf.add_page()
fpdf.set_font('Times', size = 12)
fpdf.multi_cell(0, 12, 'FIREcalc Simulation Results', 0, 'C')
fpdf.multi_cell(0, 11, text1, 0, 'L')
fpdf.image('plot1.png', (a4_size[0]/2)-figure_size/2, fpdf.get_y(), w = figure_size)
fpdf.set_y(fpdf.get_y() + figure_size*.75)
fpdf.multi_cell(0, 11, text2, 0, 'L')
fpdf.image('plot2.png', (a4_size[0]/2)-figure_size/2, fpdf.get_y(), w = figure_size)
fpdf.output('output.pdf')


print('''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please see output.pdf for more information.
''')



