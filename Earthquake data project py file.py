# Project: Global Seismic Trends-Earthquake Data Analysis
import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import pymysql

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

all_records = []
# data1=[]
start_year = datetime.now().year-5  # last 5 years
end_year = datetime.now().year
for i in range(start_year, end_year + 1):
    for j in range(1, 13):
        start_date = f"{i}-{j:02d}-01"
        if j == 12:
            end_date = f"{i+1}-01-01"
        else:
            end_date = f"{i}-{j+1:02d}-01"
        params={"format":"geojson","starttime":start_date,"endtime":end_date,"minmagnitude":3}
        response = requests.get(url, params=params)
        data = response.json()
        features = data.get("features",[])
        # data1.append(features)
        # print(f"{start_date} → {len(features)} events") 
                      
        for f in data["features"]:
            p = f["properties"]
            g = f["geometry"]["coordinates"]
            all_records.append({
                "id": f.get("id"),
                "time": pd.to_datetime(p.get("time"), unit="ms"),
                "updated": pd.to_datetime(p.get("updated"), unit="ms"),
                "latitude": g[1] if g else None,
                "longitude": g[0] if g else None,
                "depth_km": g[2] if g else None,
                "mag": p.get("mag"),
                "magtype": p.get("magType"),
                "place": p.get("place"),
                "status": p.get("status"),
                "tsunami": p.get("tsunami"),
                "alert": p.get("alert"),
                "felt": p.get("felt"),
                "cdi": p.get("cdi"),
                "mmi": p.get("mmi"),
                "sig": p.get("sig"),
                "net": p.get("net"),
                "code": p.get("code"),
                "ids": p.get("ids"),
                "sources":p.get("sources"),
                "types": p.get("types"),
                "nst": p.get("nst"),
                "dmin": p.get("dmin"),
                "rms": p.get("rms"),
                "gap": p.get("gap"),
                "type": p.get("type"),
                "magerror": p.get("magError"),
                "magnst": p.get("magNst"),
                "deptherror": p.get("depthError")
            })

df = pd.DataFrame(all_records)

# print("Rows:", df.shape[0])
# print("Columns:", df.shape[1])
# print(df)
# print (all_records) 
print("Data Scrapping completed")
#1. 	Load Data
# Load the dataset directly from API or CSV into Pandas.
df.to_csv("earthquakes1.csv", index=False)
df1 = pd.read_csv("earthquakes1.csv")

# Convert date/time fields (time, updated) to datetime objects.
# Year, month, day, day_of_week from time.
df1['time'] = pd.to_datetime(df1['time'])
df1['updated'] = pd.to_datetime(df1['updated'])
df1['year'] = df1['time'].dt.year
df1['month'] = df1['time'].dt.month
df1['day'] = df1['time'].dt.day
df1['day_of_week'] = df1['time'].dt.day_name()
df1['hour'] = df1['time'].dt.hour
# print(df1)
# 2.Clean Text Fields 

df1.drop(columns=['magerror','magnst','deptherror'], inplace=True)  #Dropping columns with no values

# Use Regex to extract country from place.
df1['place'] = df1['place'].str.strip() # Cleaning data

# Extract country
df1['country'] = df1['place'].str.extract(r',\s*([^,]+)$').iloc[:, 0].fillna(df1['place'])

# Direct replacement using regex - more reliable than dict mapping
replacements = [
    (r'(?i)^off the east coast of the north island of new zealand$', 'North Island of New Zealand'),
    (r'(?i)^north of ascension island$', 'Ascension Island'),
    (r'(?i)^west of macquarie island$', 'Macquarie Island'),
    (r'(?i)^southeast of the loyalty islands$', 'Loyalty Islands'),
    (r'(?i)^east of the south sandwich islands$', 'South Sandwich Islands'),
    (r'(?i)^south of the kermadec islands$', 'Kermadec Islands'),
    (r'(?i)^southeast of easter island$', 'Easter Island'),
    (r'(?i)^off the west coast of the south island of new zealand$', 'South Island of New Zealand'),
    (r'(?i)^2021 south sandwich islands earthquake$', 'South Sandwich Islands'),
    (r'(?i)^\d+ km nne of ta$', 'American Samoa Islands'),  # matches any number
    (r'(?i)^new zealand earthquake$', 'New Zealand'),
    (r'(?i)^alaska earthquake$', 'Alaska'),
    (r'(?i)^kahramanmaras earthquake sequence$', 'Kahramanmaras'),
    (r'(?i)^lake almanor earthquake$', 'Lake Almanor'),
    (r'(?i)^japan earthquake$', 'Japan'),
    (r'(?i)^new jersey earthquake$', 'New Jersey'),
    (r'(?i)^texas earthquake$', 'Texas'),
    (r'(?i)^nevada earthquake$', 'Nevada'),
    (r'(?i)^california earthquake$', 'California'),
    (r'(?i)^2025 southern tibetan plateau earthquake$', 'Southern Tibetan Plateau'),
    (r'(?i)^burma \(myanmar\) earthquake$', 'Myanmar'),
    (r'(?i)^2025 drake passage earthquake$', 'Drake Passage'),
    (r'(?i)^russia earthquake$', 'Russia'),
    (r'(?i)^2025 southern drake passage earthquake$', 'Drake Passage'),
    (r'(?i)^taiwan earthquake$', 'Taiwan'),
    (r'(?i)^2025 hubbard glacier earthquake$', 'Hubbard Glacier'),
    (r'(?i)^louisiana earthquake$', 'Louisiana'),
]

for i, j in replacements:
    df1['country'] = df1['country'].str.replace(i, j, regex=True, case=False)

# print(df1[['place', 'country']])

#●	 Normalize alert field (if exists) to lowercase.
df['alert']= df['alert'].str.lower()
df['alert'].value_counts().reset_index()

# Clean Numeric fields-Convert mag, depth_km, nst, dmin, rms, gap, magError, depthError, magNst, sig to numeric.
df1['mag'] = df1['mag'].astype(float)
df1['depth_km'] = df1['depth_km'].astype(float)
df1['nst'] = df1['nst'].astype(float)
df1['dmin'] = df1['dmin'].astype(float)
df1['rms'] = df1['rms'].astype(float)
df1['gap'] = df1['gap'].astype(float)
df1['sig'] = df1['sig'].astype(float)

#  ●	Fill missing numeric values with 0 or median if needed. 

# MMI (Modified Mercalli Intensity) is a measure of shaking felt by people and observed effects.  mean,mode and median of MMI corresponds to 3.4 which represents III (Weak): Felt indoors by a few, especially on upper floors. No damage.As mean of 3.4 is arrived from 91.5% of the data, hence filling NA values with mean/median as the null values corresponds to 8.5%of the overall values in the columns.
# print (df1['mmi'].describe())
mmi3=df1['mmi'].mode().tolist()
# print(f"the mode is: {mmi3}")
df1['mmi']=df1['mmi'].fillna(df1['mmi'].median())
# df1.isna().sum()

# RMS (Root Mean Square residuals) measures how well the earthquake’s calculated location fits the observed seismic data. all mode, mean and median of RMS corresponds to 0.65 which represents data is reliable for 99.9% data .Hence filling NA values with median as the null values corresponds less than 1% of the overall values in the columns.
# print (df1['rms'].describe())
rms3=df1['rms'].mode().tolist()
# print(f"the mode is: {rms3}")
df1['rms']=df1['rms'].fillna(df1['rms'].median())
# df1.isna().sum()

# Dmin The shortest distance (in degrees or kilometers) between the earthquake epicenter and the nearest seismic station. small is nearest and large is far away. mode is 0, mean is 3.18 and median is 1.8 arrived from 96.4% data.Hence filling NA values with median represents a “typical” distance as the difference between mode and mean is high and median is balanced.
# print (df1['dmin'].describe())
dmin3=df1['dmin'].mode().tolist()
# print(f"the mode is: {dmin3}")
df1['dmin']=df1['dmin'].fillna(df1['dmin'].median())
# df1.isna().sum()

# gap(Azimuthal Gap) is the largest angle (in degrees) between neighboring seismic stations, as seen from the epicenter. small (close to 0) is good coverage and large (close to 180) is poor coverage.
# Mean is 122.4 and median is 113 arrived from 97.3% non-null data which represents the stations are fairly relaible to record the epicentre. Mean and median Gap is moderate. hence filling null valuews with median.

# print (df1['gap'].describe())
gap3=df1['gap'].mode().tolist()
# print(f"the mode is: {gap3}")
df1['gap']=df1['gap'].fillna(df1['gap'].median())

# nst is the number of seismic stations that reported the earthquake. Higher nst: More stations → better triangulation → more reliable epicenter and depth.
# Mean is 45.4 and median is 32 arrived from 75% non-null data which represents better triangulation and many seismic stations contributed arrival‑time data.hence filling null values with median as it has less impact from high values(619.00).

# print (df1['nst'].describe())
nst3=df1['nst'].mode().tolist()
# print(f"the mode is: {nst3}")
df1['nst']=df1['nst'].fillna(df1['nst'].median())

# cdi(Community Decimal Intensity).A decimal value representing the average shaking intensity reported by the community (crowdsourced). Lower-weak shaking, felt by few.High-Strong shaking, widely felt, possible minor damage
# Mean and median is 3.2 arrived from 25% non-null data which represents low level of data relaibility.hence taking median to fill null values as mean and median are nearly equal.

# print (df1['cdi'].describe())
cd13=df1['cdi'].mode().tolist()
# print(f"mode is:{cd13}")
df1['cdi']=df1['cdi'].fillna(df1['cdi'].median())
# df1.isna().sum()

# felt.The number of people who reported feeling the earthquake. Lower-few reports, reported by few.High-more no.of.reports.
# Mean is 98 and median is 3.2 arrived from 25% non-null data which represents low level of data relaibility. As filling the null with 0 would be misrepresented with no reports, hence filing with median (as mode is very much skewed from mean and near to median).

# print (df1['felt'].describe())
felt3=df1['felt'].mode().tolist()
# print(f"Mode is :{felt3}")
df1['felt']=df1['felt'].fillna(df1['felt'].median())
df1.isna().sum()

# Alert:impact alert level. It’s a rapid estimate of the potential human and economic consequences of an earthquake, based not only on magnitude but also on population exposure, building vulnerability, and resilience of the affected area.
# print(df1['alert'].describe())
# print(df1['alert'].value_counts().reset_index())
df1['alert']=df1['alert'].fillna('Data_Not_available')
# df1.isna().sum()

print("Data cleaning completed")

# Adding derived columns from existing data
# Deriving Shallow/deep earthquake columns based on depth_km
EQ_type=[]
for i in df1['depth_km']:
    if i < 70:
        EQ_type.append('Shallow')
    elif i < 300:
        EQ_type.append('Intermediate')
    else:
        EQ_type.append('Deep')

df1['EQ_type'] = EQ_type
# print(df1)

# Deriving strong/destructive column based on mag thresholds.
EQ_intensity=[]
for i in df1['mag']:
    if i < 4:
        EQ_intensity.append('Minor')
    elif i < 5:
        EQ_intensity.append('Light')
    elif i < 6:
        EQ_intensity.append('Moderate')
    elif i < 7:
        EQ_intensity.append('Strong')
    else:
        EQ_intensity.append('Destructive')
df1['EQ_intensity']= EQ_intensity

#Adding continent column of the respective country
import pycountry
import pycountry_convert as pc

# ── STEP 1: pycountry auto-resolves clean country names (203/532 unique values)
unique_countries = df1['country'].unique()
lookup_cache = {}

for c in unique_countries:
    try:
        alpha2 = pycountry.countries.search_fuzzy(c)[0].alpha_2
        code   = pc.country_alpha2_to_continent_code(alpha2)
        lookup_cache[c] = pc.convert_continent_code_to_continent_name(code)
    except:
        lookup_cache[c] = None   # mark for keyword fallback

# ── STEP 2: Keyword fallback for regions, seas, border areas (329/532 values)
KEYWORD_MAP = {
    # NORTH AMERICA
    'alaska': 'North America', 'california': 'North America', 'nevada': 'North America',
    'oregon': 'North America', 'washington': 'North America', 'montana': 'North America',
    'idaho': 'North America', 'wyoming': 'North America', 'utah': 'North America',
    'arizona': 'North America', 'colorado': 'North America', 'new mexico': 'North America',
    'texas': 'North America', 'oklahoma': 'North America', 'kansas': 'North America',
    'nebraska': 'North America', 'south dakota': 'North America', 'north dakota': 'North America',
    'minnesota': 'North America', 'iowa': 'North America', 'missouri': 'North America',
    'arkansas': 'North America', 'louisiana': 'North America', 'mississippi': 'North America',
    'tennessee': 'North America', 'kentucky': 'North America', 'illinois': 'North America',
    'indiana': 'North America', 'ohio': 'North America', 'michigan': 'North America',
    'wisconsin': 'North America', 'florida': 'North America', 'alabama': 'North America',
    'south carolina': 'North America', 'north carolina': 'North America',
    'virginia': 'North America', 'west virginia': 'North America',
    'maryland': 'North America', 'delaware': 'North America', 'new jersey': 'North America',
    'new york': 'North America', 'connecticut': 'North America', 'maine': 'North America',
    'massachusetts': 'North America', 'pennsylvania': 'North America',
    'hawaii': 'North America', 'canada': 'North America', 'mexico': 'North America',
    'cuba': 'North America', 'haiti': 'North America', 'dominican republic': 'North America',
    'jamaica': 'North America', 'puerto rico': 'North America', 'virgin islands': 'North America',
    'leeward islands': 'North America', 'trinidad': 'North America', 'barbados': 'North America',
    'grenada': 'North America', 'dominica': 'North America', 'saint lucia': 'North America',
    'saint kitts': 'North America', 'saint vincent': 'North America',
    'saint eustatius': 'North America', 'anguilla': 'North America',
    'antigua': 'North America', 'guadeloupe': 'North America', 'martinique': 'North America',
    'cayman islands': 'North America', 'bermuda': 'North America', 'bahamas': 'North America',
    'belize': 'North America', 'guatemala': 'North America', 'honduras': 'North America',
    'el salvador': 'North America', 'nicaragua': 'North America', 'costa rica': 'North America',
    'panama': 'North America', 'saint pierre': 'North America', 'greenland': 'North America',
    'aleutian islands': 'North America', 'queen charlotte': 'North America',
    'vancouver island': 'North America', 'united states': 'North America',
    'revilla gigedo': 'North America', 'gulf of america': 'North America',
    'ak': 'North America', 'ca': 'North America', 'nv': 'North America',
    'or': 'North America', 'wa': 'North America', 'mx': 'North America',

    # SOUTH AMERICA
    'colombia': 'South America', 'venezuela': 'South America', 'guyana': 'South America',
    'suriname': 'South America', 'brazil': 'South America', 'ecuador': 'South America',
    'peru': 'South America', 'bolivia': 'South America', 'chile': 'South America',
    'argentina': 'South America', 'paraguay': 'South America', 'uruguay': 'South America',
    'falkland islands': 'South America', 'south georgia': 'South America',
    'galapagos': 'South America', 'easter island': 'South America',

    # EUROPE
    'iceland': 'Europe', 'norway': 'Europe', 'sweden': 'Europe', 'finland': 'Europe',
    'denmark': 'Europe', 'united kingdom': 'Europe', 'ireland': 'Europe',
    'portugal': 'Europe', 'spain': 'Europe', 'france': 'Europe', 'netherlands': 'Europe',
    'belgium': 'Europe', 'germany': 'Europe', 'switzerland': 'Europe', 'austria': 'Europe',
    'italy': 'Europe', 'malta': 'Europe', 'greece': 'Europe', 'albania': 'Europe',
    'north macedonia': 'Europe', 'serbia': 'Europe', 'croatia': 'Europe',
    'bosnia': 'Europe', 'montenegro': 'Europe', 'hungary': 'Europe',
    'slovakia': 'Europe', 'poland': 'Europe', 'romania': 'Europe', 'bulgaria': 'Europe',
    'ukraine': 'Europe', 'belarus': 'Europe', 'estonia': 'Europe', 'latvia': 'Europe',
    'lithuania': 'Europe', 'kosovo': 'Europe', 'svalbard': 'Europe',
    'jan mayen': 'Europe', 'reykjanes': 'Europe', 'azores': 'Europe',

    # AFRICA
    'morocco': 'Africa', 'algeria': 'Africa', 'tunisia': 'Africa', 'libya': 'Africa',
    'egypt': 'Africa', 'mauritania': 'Africa', 'chad': 'Africa', 'sudan': 'Africa',
    'south sudan': 'Africa', 'ethiopia': 'Africa', 'eritrea': 'Africa',
    'djibouti': 'Africa', 'somalia': 'Africa', 'kenya': 'Africa', 'uganda': 'Africa',
    'rwanda': 'Africa', 'burundi': 'Africa',
    'democratic republic of the congo': 'Africa', 'congo': 'Africa',
    'gabon': 'Africa', 'angola': 'Africa', 'zambia': 'Africa', 'malawi': 'Africa',
    'mozambique': 'Africa', 'zimbabwe': 'Africa', 'botswana': 'Africa',
    'namibia': 'Africa', 'south africa': 'Africa', 'madagascar': 'Africa',
    'tanzania': 'Africa', 'ghana': 'Africa', 'nigeria': 'Africa', 'cape verde': 'Africa',
    'saint helena': 'Africa', 'ascension island': 'Africa', 'tristan da cunha': 'Africa',
    'mayotte': 'Africa', 'mauritius': 'Africa', 'seychelles': 'Africa',
    'prince edward islands': 'Africa', 'crozet islands': 'Africa', 'kerguelen': 'Africa',
    'bouvet': 'Africa', 'guinea': 'Africa',

    # ASIA
    'turkey': 'Asia', 'kahramanmaras': 'Asia', 'syria': 'Asia', 'lebanon': 'Asia',
    'israel': 'Asia', 'jordan': 'Asia', 'iraq': 'Asia', 'iran': 'Asia',
    'saudi arabia': 'Asia', 'yemen': 'Asia', 'oman': 'Asia',
    'united arab emirates': 'Asia', 'qatar': 'Asia', 'kuwait': 'Asia',
    'cyprus': 'Asia', 'armenia': 'Asia', 'azerbaijan': 'Asia',
    'turkmenistan': 'Asia', 'uzbekistan': 'Asia', 'kazakhstan': 'Asia',
    'kyrgyzstan': 'Asia', 'tajikistan': 'Asia', 'afghanistan': 'Asia',
    'pakistan': 'Asia', 'india': 'Asia', 'nepal': 'Asia', 'bhutan': 'Asia',
    'bangladesh': 'Asia', 'sri lanka': 'Asia', 'maldives': 'Asia',
    'myanmar': 'Asia', 'burma': 'Asia', 'thailand': 'Asia', 'laos': 'Asia',
    'vietnam': 'Asia', 'cambodia': 'Asia', 'malaysia': 'Asia', 'indonesia': 'Asia',
    'timor': 'Asia', 'philippines': 'Asia', 'philippine islands': 'Asia',
    'china': 'Asia', 'taiwan': 'Asia', 'mongolia': 'Asia',
    'north korea': 'Asia', 'south korea': 'Asia', 'japan': 'Asia',
    'kuril islands': 'Asia', 'russia': 'Asia', 'xinjiang': 'Asia',
    'xizang': 'Asia', 'tibetan': 'Asia', 'kashmir': 'Asia', 'socotra': 'Asia',
    'severnaya zemlya': 'Asia', 'georgia': 'Asia',

    # OCEANIA
    'australia': 'Oceania', 'new zealand': 'Oceania', 'papua new guinea': 'Oceania',
    'solomon islands': 'Oceania', 'santa cruz islands': 'Oceania',
    'vanuatu': 'Oceania', 'fiji': 'Oceania', 'tonga': 'Oceania',
    'samoa': 'Oceania', 'kiribati': 'Oceania', 'micronesia': 'Oceania',
    'palau': 'Oceania', 'guam': 'Oceania', 'mariana islands': 'Oceania',
    'new caledonia': 'Oceania', 'wallis and futuna': 'Oceania',
    'french polynesia': 'Oceania', 'pitcairn': 'Oceania', 'cook islands': 'Oceania',
    'kermadec': 'Oceania', 'macquarie': 'Oceania', 'loyalty islands': 'Oceania',
    "d'entrecasteaux": 'Oceania', 'bismarck sea': 'Oceania', 'Ta': 'Oceania',

    # ANTARCTICA
    'antarctica': 'Antarctica', 'south shetland': 'Antarctica',
    'south sandwich': 'Antarctica', 'balleny': 'Antarctica',
    'drake': 'Antarctica', 'scotia sea': 'Antarctica',
    'west chile rise': 'Antarctica', 'hubbard glacier': 'Antarctica',
}

OCEAN_WORDS = [
    'ocean', 'sea', 'ridge', 'rise', 'strait', 'passage', 'gulf', 'bay',
    'channel', 'fracture zone', 'arctic', 'atlantic', 'pacific', 'bering',
    'beaufort', 'labrador', 'norwegian', 'laptev', 'davis', 'lomonosov',
    'carlsberg', 'chagos', 'mid-', 'arafura', 'banda', 'savu', 'flores',
    'molucca', 'celebes', 'laccadive', 'ionian', 'adriatic', 'aegean',
    'ligurian', 'caspian'
]

SORTED_KEYS = sorted(KEYWORD_MAP.keys(), key=len, reverse=True)  # longest-match first

def keyword_fallback(s):
    sl = s.lower()
    for kw in SORTED_KEYS:
        if kw in sl: return KEYWORD_MAP[kw]
    for ow in OCEAN_WORDS:
        if ow in sl: return 'Ocean/Other'
    return 'unknown'

for c, val in lookup_cache.items():
    if val is None:
        lookup_cache[c] = keyword_fallback(str(c))

# ── STEP 3: O(1) dict lookup per row — fastest possible for 112K rows
df1['continent'] = df1['country'].map(lookup_cache)

# export as csv
df1.to_csv("EQ_finaldata.csv", index=False)

print("Final CSV export completed")

# Transferring data to sql DB

print("Starting data upload to SQL database...")
# --- Create database ---
try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='Mwin@2028')
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS EQ1;")
    cursor.close()
    conn.close()
    print("Database EQ1 created successfully, uploading the data from csv to SQL DB...")
except Exception as e:
    print(" Error while creating DB:", e)

engine = create_engine('mysql+pymysql://root:Mwin%402028@127.0.0.1:3306/EQ1')
df2 = pd.read_csv("EQ_finaldata.csv")
df2.to_sql("EQ_data", engine, if_exists='replace', index=False)
print(f"Uploaded {len(df2)} rows to databse EQ")
print("Data upload to SQL completed")
