import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from collections import namedtuple
from matplotlib.lines import Line2D

DATA = "/Users/anton_grahed/Desktop/Macroeconomics/Quantitative Macro/datasets"
data = pd.read_excel(os.path.join(DATA, "mpd2020.xlsx"), sheet_name= 'Full data')

# how many countries are in 
len(data.country.unique())

# for each country: what years are available?
## manual method
cntry_years = []
for cntry in data.country.unique():
    cy_data = data[data.country == cntry]['year']
    ymin, ymax = cy_data.min(), cy_data.max()
    cntry_years.append((cntry, ymin, ymax))
# put in a dataframe
cntry_years = pd.DataFrame(cntry_years, columns=['country', 'min', 'max'])

cntry_years

## reshape data 
# 1. map between country-code and country

# whenever you filter: index will change 
# drop = True means that the index is reset
code_to_name = data[['countrycode', 'country']].drop_duplicates().reset_index(drop=True).set_index(['countrycode'])

# focus on GDP 
gdppc = data.set_index(['countrycode', 'year'])['gdppc']

# now we can unstack based on countrycode
gdppc = gdppc.unstack('countrycode')

# create a colormap b/w country codes and colors for consistency
country_names = data['countrycode']

colors = cm.tab20(np.linspace(0, 0.95, len(country_names)))

# Create a dictionary to map each country to its corresponding color
color_mapping = {country: color for country, color in zip(country_names, colors)}

## GPD FOR UK
fig, ax = plt.subplots(dpi=300)
cntry = "GBR"
_ = gdppc[cntry].plot(
    ax = fig.gca(), # get current axes
    ylabel = "International $\'s",
    xlabel = "Year",
    linestyle = "-",
    color = color_mapping[cntry]
)

# can interpolate to fill in gaps
fig, ax = plt.subplots(dpi=300)
cntry = "GBR"

# interpolated plot 
ax.plot(gdppc[cntry].interpolate(),
        linestyle = "--",
        color = color_mapping[cntry],
        lw = 2)

ax.plot(gdppc[cntry],
        linestyle = "-",
        color = color_mapping[cntry],
        lw = 2)
ax.set_ylabel("International $'s")
ax.set_xlabel("Year")
plt.show()

## now make a function 
def draw_interp_plots(series, ylabel, xlabel, color_mapping, code_to_name, lw, logscale, ax):
    for i,c in enumerate(cntry):
        # get the interpolated data 
        df_interpolated = series[c].interpolate(limit_area = "inside")
        interpolated_data = df_interpolated[series[c].isnull()]

        # plot the interpolated data
        ax.plot(interpolated_data,
                linestyle='--',
                lw=lw,
                alpha=0.7,
                color=color_mapping[c])
        
        # Plot the non-interpolated data with solid lines
        ax.plot(series[c],
                linestyle='-',
                lw=lw,
                color=color_mapping[c],
                alpha=0.8,
                label=code_to_name.loc[c]['country'])
        
        # add option of logscale 
        if logscale == True: 
            ax.set_yscale('log')

    # draw legend outside plot 
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    
    return ax



## allows us to make really nice plots: US, GBR, CHN

# we want to highlight events: define a namedtuple for it
Event = namedtuple("Event", ["year_range", "y_text", "text", "color", "ymax"])

fig, ax = plt.subplots(dpi=300, figsize = (10, 6))

cntry = ["CHN", "GBR", "USA"]
ax = draw_interp_plots(gdppc[cntry].loc[1500:], # plot from 1500 onwards - year is index 
                       "International $'s", "Year",
                       color_mapping, code_to_name, 2, False, ax)


# Define the parameters for the events and the text
ylim = ax.get_ylim()[1]
b_params = {'color':'grey', 'alpha': 0.2}
t_params = {'fontsize': 9, 
            'va':'center', 'ha':'center'}

# Create a list of events to annotate
events = [
    Event((1650, 1652), ylim + ylim*0.04, 
          'the Navigation Act\n(1651)',
          color_mapping['GBR'], 1),
    Event((1655, 1684), ylim + ylim*0.13, 
          'Closed-door Policy\n(1655-1684)', 
          color_mapping['CHN'], 1.1),
    Event((1848, 1850), ylim + ylim*0.22,
          'the Repeal of Navigation Act\n(1849)', 
          color_mapping['GBR'], 1.18),
    Event((1765, 1791), ylim + ylim*0.04, 
          'American Revolution\n(1765-1791)', 
          color_mapping['USA'], 1),
    Event((1760, 1840), ylim + ylim*0.13, 
          'Industrial Revolution\n(1760-1840)', 
          'grey', 1.1),
    Event((1929, 1939), ylim + ylim*0.04, 
          'the Great Depression\n(1929–1939)', 
          'grey', 1),
    Event((1978, 1979), ylim + ylim*0.13, 
          'Reform and Opening-up\n(1978-1979)', 
          color_mapping['CHN'], 1.1)
]

# draw events 
def draw_events(events, ax):
    # iterate over events
    for event in events:
        event_mid = sum(event.year_range) / 2 # evetn midpoint
        ax.text(event_mid,
                event.y_text,
                event.text,
                color = event.color,
                **t_params) # unpack dictionary - pass k-v pairs as keyword arguments
        ax.axvspan(*event.year_range, # unpack tuple into separate arguments
                   color = event.color,
                   alpha = 0.2)
        ax.axvline(event_mid, ymin = 1,
                   ymax = event.ymax, color = event.color,
                   linestyle = "-", clip_on = False, alpha = 0.15)

# draw events
draw_events(events, ax) 
plt.show()

