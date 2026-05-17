import wikipediaapi
import os

wiki = wikipediaapi.Wikipedia('IPLRAG/1.0', 'en')

topics = [
    # General IPL
    "Indian Premier League", "IPL auction", "IPL records",
    "Duckworth–Lewis–Stern method",

    # All seasons
    "2008 Indian Premier League", "2009 Indian Premier League",
    "2010 Indian Premier League", "2011 Indian Premier League",
    "2012 Indian Premier League", "2013 Indian Premier League",
    "2014 Indian Premier League", "2015 Indian Premier League",
    "2016 Indian Premier League", "2017 Indian Premier League",
    "2018 Indian Premier League", "2019 Indian Premier League",
    "2020 Indian Premier League", "2021 Indian Premier League",
    "2022 Indian Premier League", "2023 Indian Premier League",
    "2024 Indian Premier League",

    # All teams
    "Mumbai Indians", "Chennai Super Kings", "Royal Challengers Bangalore",
    "Kolkata Knight Riders", "Sunrisers Hyderabad", "Delhi Capitals",
    "Rajasthan Royals", "Punjab Kings", "Lucknow Super Giants",
    "Gujarat Titans", "Deccan Chargers", "Kochi Tuskers Kerala",
    "Pune Warriors India", "Rising Pune Supergiant",

    # Top players
    "MS Dhoni", "Rohit Sharma", "Virat Kohli", "Sachin Tendulkar",
    "Sourav Ganguly", "Rahul Dravid", "AB de Villiers", "Chris Gayle",
    "David Warner", "Kane Williamson", "Jos Buttler", "Suresh Raina",
    "Yusuf Pathan", "Irfan Pathan", "Harbhajan Singh", "Lasith Malinga",
    "Jasprit Bumrah", "Hardik Pandya", "Krunal Pandya", "Kieron Pollard",
    "Andre Russell", "Sunil Narine", "Shakib Al Hasan", "Dwayne Bravo",
    "Ravindra Jadeja", "Ravichandran Ashwin", "Shane Watson",
    "Adam Gilchrist", "Brendon McCullum", "Kevin Pietersen",
    "Gautam Gambhir", "Virender Sehwag", "Yuvraj Singh", "Robin Uthappa",
    "Dinesh Karthik", "Shreyas Iyer", "Shubman Gill", "Rishabh Pant",
    "KL Rahul", "Mayank Agarwal", "Prithvi Shaw", "Ishan Kishan",

    # Venues
    "Wankhede Stadium", "Eden Gardens", "M. Chinnaswamy Stadium",
    "Feroz Shah Kotla", "MA Chidambaram Stadium", "Rajiv Gandhi International Cricket Stadium",
    "Sawai Mansingh Stadium", "Punjab Cricket Association Stadium",
    "Dubai International Cricket Stadium", "Sharjah Cricket Stadium",

   # IPL related
    "IPL 2025", "IPL media rights", "IPL team owners",
    "Mukesh Ambani", "N. Srinivasan", "Lalit Modi",
    "BCCI", "Cricket South Africa", "England and Wales Cricket Board",

  # Coaches and admins
    "Ricky Ponting", "Stephen Fleming", "Andy Flower",
    "Board of Control for Cricket in India",

 # More venues
    "Narendra Modi Stadium", "Holkar Cricket Stadium",
    "JSCA International Stadium Complex",
    "Maharashtra Cricket Association Stadium",
    "Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium",  


# Cricket general pages (lots of text)
    "Cricket", "Test cricket", "One Day International",
    "Twenty20 cricket", "Twenty20 International",
    "Cricket statistics", "List of IPL records",
    "History of cricket", "Cricket in India",
    "Board of Control for Cricket in India",
    "Cricket World Cup", "ICC World Twenty20",

  # More players
    "Virat Kohli", "Sachin Tendulkar biography", "Sanju Samson",
    "Ambati Rayudu", "Faf du Plessis", "Quinton de Kock",
    "Nicholas Pooran", "Trent Boult", "Pat Cummins",
    "Mitchell Starc", "Glenn Maxwell", "David Miller",
    "Lendl Simmons", "Eoin Morgan", "Jason Roy",
    "Sam Curran", "Ben Stokes", "Jonny Bairstow",



# Recent star players
    "Abhishek Sharma cricketer", "Yashasvi Jaiswal",
    "Tilak Varma", "Rinku Singh cricketer",
    "Shubman Gill", "Ruturaj Gaikwad",
    "Devdutt Padikkal", "Prithvi Shaw",
    "Ishan Kishan", "Sai Sudharsan",
    "Rajat Patidar", "Deepak Hooda",
    "Axar Patel", "Washington Sundar",
    "Ravi Bishnoi", "Avesh Khan",
    "Arshdeep Singh", "Umran Malik",
    "Mohammed Siraj", "Prasidh Krishna",
    "Kuldeep Yadav", "Yuzvendra Chahal",
    "Deepak Chahar", "Shardul Thakur",
    "Rahul Tewatia", "Shimron Hetmyer",
    "Heinrich Klaasen", "Marco Jansen",
    "Phil Salt", "Travis Head",
    "Mitchell Marsh", "Jake Fraser-McGurk",
    "Tristan Stubbs", "Gerald Coetzee",
    "Alzarri Joseph", "Akeal Hosein",


# IPL Auctions
    "2008 Indian Premier League Player Auction",
    "2011 IPL auction", "2014 IPL auction",
    "2018 IPL auction", "2021 IPL auction",
    "2022 IPL mega auction", "2023 IPL auction",
    "2024 IPL auction", "2025 IPL auction",
    "IPL retention rules", "Right to Match card IPL",

# Team owners
    "Mukesh Ambani", "Nita Ambani",
    "N. Srinivasan", "Kalanithi Maran",
    "Kavya Maran", "Parth Jindal",
    "Sanjiv Goenka", "Manoj Badale",
    "Ness Wadia", "Mohit Burman",
    "Irfan Razack", "Sameer Mehta",
    "CVC Capital Partners", "RPSG Group",
    "Torrent Group", "Kotak Mahindra",

    # Media rights
    "Star Sports India", "Disney Plus Hotstar",
    "Jio Cinema", "Sony Sports Network",
    "IPL broadcasting rights", "BCCI media rights deal",
    "Viacom18", "Star India",

    # Records and stats
    "List of Indian Premier League records",
    "List of IPL centuries", "IPL highest score",
    "IPL most wickets", "IPL orange cap winners",
    "IPL purple cap winners", "IPL most valuable player",
    "IPL highest team score", "IPL lowest team score",
    "IPL hat tricks", "IPL super overs",
    "IPL playoff records", "IPL final results",
    "List of IPL hat-tricks",
    "List of IPL award winners",

]

os.makedirs("ipl_data", exist_ok=True)
all_text = ""

for topic in topics:
    page = wiki.page(topic)
    if page.exists():
        print(f"Fetching: {topic}")
        all_text += f"\n\n=== {topic} ===\n{page.text}"
    else:
        print(f"Skipped (not found): {topic}")

with open("ipl_data/ipl_corpus.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"\nDone! Total characters: {len(all_text)}")
